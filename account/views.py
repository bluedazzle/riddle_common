# coding: utf-8
from __future__ import unicode_literals

import random
import string
import uuid 

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views.generic import CreateView, ListView
from django.views.generic import DetailView
from django.views.generic import FormView

from account.forms import VerifyCodeForm, ValidateVerifyCodeForm
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from account.models import User
from core.sms import send_sms_by_phone
from core.wx import get_access_token_by_code, get_user_info, send_money_by_open_id
from core.consts import DEFAULT_SONGS_BONUS_THRESHOLD, STATUS_REVIEW, STATUS_FINISH, STATUS_FAIL
from core.dss.Serializer import serializer
from finance.models import CashRecord


class UserInfoView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, DetailView):
    model = User
    slug_field = 'token'
    datetime_type = 'timestamp'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        self.kwargs['slug'] = self.token
        return super(UserInfoView, self).get(self, request, *args, **kwargs)


class UserRegisterView(StatusWrapMixin, FormJsonResponseMixin, CreateView):
    model = User
    count = 32
    http_method_names = ['post']
    datetime_type = 'timestamp'

    def post(self, request, *args, **kwargs):
        device_id = request.POST.get('device_id', '')
        user = User()
        user.device_id = device_id
        user.token = self.create_token()
        user.name = self.create_name()
        user.expire_time = timezone.now() + datetime.timedelta(days=3)
        invite_code = self.create_invite_code()
        objs = self.model.objects.filter(invite_code=invite_code).all()
        while objs.exists():
            invite_code = self.create_invite_code()
            objs = self.model.objects.filter(invite_code=invite_code).all()
        user.invite_code = invite_code
        user.save()
        return self.render_to_response({'user': user})

    @staticmethod
    def create_name():
        name = '游客' + ''.join(random.sample('1234567890', 7)).replace(" ", "")
        return name

    def create_token(self):
        token = ''.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        return token

    def create_invite_code(self):
        invite_code = ''.join(
            random.sample('1234567890ZYXWVUTSRQPONMLKJIHGFEDCBAZYXWVUTSRQPONMLKJIHGFEDCBA', 8)).replace(" ", "")
        return invite_code


class WxLoginView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    force_check = False
    model = User
    slug_field = 'wx_open_id'
    datetime_type = 'timestamp'

    # http_method_names = ['post']

    def get(self, request, *args, **kwargs):
        try:
            code = request.GET.get('code')
            if not code:
                self.update_status(StatusCode.ERROR_PARAMETER)
                return self.render_to_response()
            data = get_access_token_by_code(code)
            wx_open_id = data.get('openid')
            self.slug_field = 'wx_open_id'
            self.kwargs['slug'] = wx_open_id
            obj = None
            try:
                obj = self.get_object()
            except Http404:
                pass
            if obj:
                return self.render_to_response({'user': obj})
            access_token = data.get('access_token')
            if not wx_open_id or not access_token:
                self.update_status(StatusCode.ERROR_PARAMETER)
                return self.render_to_response()
            data = get_user_info(access_token, wx_open_id)
            name = data.get('nickname').encode('raw_unicode_escape').decode()
            avatar = data.get('headimgurl')
            province = data.get('province').encode('raw_unicode_escape').decode()
            city = data.get('city').encode('raw_unicode_escape').decode()
            sex = data.get('sex')
            if not self.user:
                self.update_status(StatusCode.ERROR_PERMISSION_DENIED)
                return self.render_to_response()
            self.user.wx_open_id = wx_open_id
            self.user.name = name if name else self.user.name
            self.user.avatar = avatar if avatar else self.user.avatar
            self.user.province = province
            self.user.city = city
            self.user.sex = sex
            self.user.save()
            return self.render_to_response({'user': self.user})
        except Exception as e:
            self.update_status(StatusCode.ERROR_DATA)
            return self.render_to_response(extra={'error': e.message})


class VerifyCodeView(CheckTokenMixin, StatusWrapMixin, FormJsonResponseMixin, FormView):
    form_class = VerifyCodeForm

    @staticmethod
    def create_code():
        return ''.join(random.sample('1234567890', 4)).replace(" ", "")

    @staticmethod
    def check_exist(phone):
        objs = User.objects.filter(phone=phone).all()
        if objs.exists():
            return True
        return False

    def form_valid(self, form):
        if self.user.phone:
            self.update_status(StatusCode.ERROR_PHONE_BIND)
            return self.render_to_response()
        phone = form.cleaned_data.get('phone')
        if self.check_exist(phone):
            self.update_status(StatusCode.ERROR_PHONE_EXIST)
            return self.render_to_response()
        try:
            from core.cache import set_verify_to_redis
            code = self.create_code()
            send_sms_by_phone(phone, code)
            set_verify_to_redis(code, phone)
            return self.render_to_response()
        except Exception as e:
            self.update_status(StatusCode.ERROR_DATA)
            return self.render_to_response(extra={'error': e.message})


class ValidateVerifyView(CheckTokenMixin, StatusWrapMixin, FormJsonResponseMixin, FormView):
    form_class = ValidateVerifyCodeForm

    @staticmethod
    def check_exist(phone):
        objs = User.objects.filter(phone=phone).all()
        if objs.exists():
            return True
        return False

    def form_valid(self, form):
        from core.cache import get_verify_from_redis
        if self.user.phone:
            self.update_status(StatusCode.ERROR_PHONE_BIND)
            return self.render_to_response()
        phone = form.cleaned_data.get('phone')
        if self.check_exist(phone):
            self.update_status(StatusCode.ERROR_PHONE_EXIST)
            return self.render_to_response()
        code = form.cleaned_data.get('code')
        verify = get_verify_from_redis(phone)
        if not verify:
            self.update_status(StatusCode.ERROR_NO_VERIFY)
            return self.render_to_response()
        if str(verify) != code:
            self.update_status(StatusCode.ERROR_VERIFY)
            return self.render_to_response()
        self.user.phone = phone
        self.user.save()
        return self.render_to_response()


class UserShareView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = User

    def get_queryset(self):
        objs = self.model.objects.filter(inviter=self.user).all()
        return objs

    def get_context_data(self, **kwargs):
        context = super(UserShareView, self).get_context_data(**kwargs)
        context['user_list'] = serializer(context['user_list'], output_type='raw', include_attr=('name', 'avatar', 'cash', 'current_level', 'id', 'right_count', 'login_bonus', 'songs_bonus'))
        context['invite_code'] = self.user.invite_code
        context['song_threshold'] = DEFAULT_SONGS_BONUS_THRESHOLD
        return context


class InviteKeyView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        if self.user.inviter:
            self.update_status(StatusCode.ERROR_INVITE_EXIST)
            return self.render_to_response()
        invite_code = request.GET.get('invite_code', '')
        objs = self.model.objects.filter(invite_code=invite_code).all()
        if not objs.exists():
            self.update_status(StatusCode.ERROR_INVITE_CODE)
            return self.render_to_response()
        if self.user.create_time <= objs[0].create_time:
            self.update_status(StatusCode.ERROR_INVITER_CODE)
            return self.render_to_response()
        self.user.inviter = objs[0]
        self.user.save()
        return self.render_to_response()


class InviteBonusView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = User

    def create_cash_record(self, cash=30):
        uid = str(uuid.uuid1())
        suid = ''.join(uid.split('-'))
        cash_record = CashRecord()
        cash_record.cash = cash
        cash_record.belong = self.user
        cash_record.status = STATUS_REVIEW
        cash_record.cash_type = '邀请注册红包提现'
        cash_record.reason = '审核中'
        cash_record.trade_no = suid
        resp = send_money_by_open_id(suid, self.user.wx_open_id, cash)
        result = False
        if resp.get('result_code') == 'SUCCESS':
            cash_record.reason = '成功'
            cash_record.status = STATUS_FINISH
            result = True
        else:
            fail_message = resp.get('err_code_des', 'default_error')
            cash_record.reason = fail_message
            cash_record.status = STATUS_FAIL
        return cash_record, result

    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid', '')
        bonus = request.GET.get('bonus', '')
        cash = 30 + random.randint(0, 5)
        cr = None
        objs = self.model.objects.filter(id=uid).all()
        if not objs.exists() or (bonus != 'login' and bonus != 'songs'):
            self.update_status(StatusCode.ERROR_INVITE_BONUS)
            return self.render_to_response()
        invite_user = objs[0]
        if bonus == 'login':
            if invite_user.login_bonus:
                self.update_status(StatusCode.ERROR_BONUS_OVER)
            else:
                cr, result = self.create_cash_record(cash=cash)
                if not result:
                    self.update_status(StatusCode.ERROR_DATA)
                    self.message = cr.reason
                else:
                    invite_user.login_bonus = True
                    invite_user.save()
                cr.save()
        if bonus == 'songs':
            if invite_user.songs_bonus:
                self.update_status(StatusCode.ERROR_BONUS_OVER)
            elif invite_user.current_level < DEFAULT_SONGS_BONUS_THRESHOLD:
                self.update_status(StatusCode.ERROR_BONUS_LESS)
            else:
                cr, result = self.create_cash_record(cash=cash)
                if not result:
                    self.update_status(StatusCode.ERROR_DATA)
                    self.message = cr.reason
                else:
                    invite_user.songs_bonus = True
                    invite_user.save()
                cr.save()
        return self.render_to_response({
            "type": 5,   # 即时到账红包
            "amount": cash,
            "other_rewards": [
                { "type": 1, "amount": 2000 },   # 红包
                { "type": 4, "amount": 20000 },  # 提现卡
            ],
        })
