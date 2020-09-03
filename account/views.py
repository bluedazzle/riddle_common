# coding: utf-8
from __future__ import unicode_literals

import random
import string

import datetime
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import FormView

from account.forms import VerifyCodeForm, ValidateVerifyCodeForm
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from account.models import User
from core.sms import send_sms_by_phone
from core.wx import get_access_token_by_code, get_user_info


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
        user.save()
        return self.render_to_response({'user': user})

    @staticmethod
    def create_name():
        name = '游客' + string.join(random.sample('1234567890', 7)).replace(" ", "")
        return name

    def create_token(self):
        token = string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        return token


class WxLoginView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    force_check = False
    # http_method_names = ['post']

    def get(self, request, *args, **kwargs):
        try:
            code = request.GET.get('code')
            if not code:
                self.update_status(StatusCode.ERROR_PARAMETER)
                return self.render_to_response()
            data = get_access_token_by_code(code)
            wx_open_id = data.get('unionid')
            self.slug_field = 'wx_open_id'
            kwargs['wx_open_id'] = wx_open_id
            obj = self.get_object()
            if obj:
                return self.render_to_response({'user': obj})
            access_token = data.get('access_token')
            if not wx_open_id and not access_token:
                self.update_status(StatusCode.ERROR_PARAMETER)
                return self.render_to_response()
            data = get_user_info(access_token, wx_open_id)
            name = data.get('nickname')
            avatar = data.get('headimgurl')
            province = data.get('province')
            city = data.get('city')
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
        return string.join(random.sample('1234567890', 4)).replace(" ", "")

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
        if unicode(verify) != code:
            self.update_status(StatusCode.ERROR_VERIFY)
            return self.render_to_response()
        self.user.phone = phone
        self.user.save()
        return self.render_to_response()
