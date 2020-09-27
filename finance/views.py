# coding: utf-8
from __future__ import unicode_literals

# Create your views here.
import random
import uuid

from django.core.exceptions import ValidationError
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.db import transaction

from baseconf.models import WithdrawConf
from core.Mixin.JsonRequestMixin import JsonRequestMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.cache import REWARD_KEY, client_redis_riddle
from core.consts import DEFAULT_ALLOW_CASH_COUNT, STATUS_USED, PACKET_TYPE_CASH, PACKET_TYPE_WITHDRAW, \
    DEFAULT_NEW_PACKET, DEFAULT_ALLOW_CASH_RIGHT_COUNT, STATUS_FAIL, STATUS_REVIEW, STATUS_FINISH, \
    DEFAULT_MAX_CASH_LIMIT
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from core.utils import get_global_conf
from core.wx import send_money_by_open_id
from finance.forms import CashRecordForm, ExchangeRecordForm
from finance.models import CashRecord, ExchangeRecord, RedPacket


class CashRecordListView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = CashRecord
    slug_field = 'token'
    paginate_by = 2
    ordering = ('-create_time',)
    datetime_type = 'string'

    def get_list_by_user(self):
        self.queryset = self.model.objects.filter(belong=self.user)

    def get_queryset(self):
        self.get_list_by_user()
        return super(CashRecordListView, self).get_queryset()


class ExchangeRecordListView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = ExchangeRecord
    slug_field = 'token'
    paginate_by = 2
    ordering = ('-create_time',)
    datetime_type = 'timestamp'

    def get_list_by_user(self):
        self.queryset = self.model.objects.filter(belong=self.user)

    def get_queryset(self):
        self.get_list_by_user()
        return super(ExchangeRecordListView, self).get_queryset()


class CreateCashRecordView(CheckTokenMixin, StatusWrapMixin, JsonRequestMixin, FormJsonResponseMixin, CreateView):
    form_class = CashRecordForm
    http_method_names = ['post']
    conf = {}

    def valid_withdraw(self, cash):
        self.conf = get_global_conf()
        if not self.user.wx_open_id:
            raise ValidationError('请绑定微信后提现')
        conf = get_global_conf()
        allow = int(conf.get('allow_cash_right_number', DEFAULT_ALLOW_CASH_RIGHT_COUNT))
        obj = WithdrawConf.objects.all()[0]
        if cash == obj.new_withdraw_threshold:
            if self.user.current_level < 11:
                raise ValidationError('答题10道即可提现')
            if not self.user.new_withdraw:
                self.user.new_withdraw = True
                return True
            else:
                raise ValidationError('新人提现机会已使用')
        if cash != obj.withdraw_first_threshold and cash != obj.withdraw_second_threshold and cash != obj.withdraw_third_threshold:
            raise ValidationError('非法的提现金额')
        if self.user.cash < obj.withdraw_first_threshold:
            raise ValidationError('提现可用金额不足')
        if self.user.right_count < allow:
            raise ValidationError('''抱歉
您还没有获得提现机会
您可以通过以下方式获得提现机会
1. 通过答题参与抽奖
2. 答对{0}道题

当前已答对{1}道'''.format(self.conf.get('allow_cash_right_number', DEFAULT_ALLOW_CASH_RIGHT_COUNT), self.user.right_count))
        raise ValidationError('体现')

    @transaction.atomic()
    def form_valid(self, form):
        uid = str(uuid.uuid1())
        suid = ''.join(uid.split('-'))
        cash = form.cleaned_data.get('cash', 0)
        try:
            self.valid_withdraw(cash)
        except Exception as e:
            self.update_status(StatusCode.ERROR_FORM)
            return self.render_to_response(extra={"error": e.message})
        super(CreateCashRecordView, self).form_valid(form)
        cash_record = form.save()
        cash_record.belong = self.user
        cash_record.status = STATUS_REVIEW
        cash_record.reason = '审核中'
        cash_record.trade_no = suid
        if cash == 30:
            resp = send_money_by_open_id(suid, self.user.wx_open_id, cash)
            if resp.get('result_code') == 'SUCCESS':
                self.user.cash -= cash
                cash_record.reason = '成功'
                cash_record.status = STATUS_FINISH
            else:
                fail_message = resp.get('err_code_des', 'default_error')
                cash_record.reason = fail_message
                cash_record.status = STATUS_FAIL
                obj = WithdrawConf.objects.all()[0]
                if cash == obj.new_withdraw_threshold:
                    self.user.new_withdraw = False
        cash_record.save()
        self.user.save()
        return self.render_to_response(dict())


class CreateExchangeRecordView(CheckTokenMixin, StatusWrapMixin, JsonRequestMixin, FormJsonResponseMixin, CreateView):
    form_class = ExchangeRecordForm
    http_method_names = ['post']
    conf = {}

    def exchange_cash(self, coin):
        # todo 可能需要分布式锁
        self.conf = get_global_conf()
        coin_cash_proportion = self.conf.get('coin_cash_proportion', 1000)
        current_coin = self.user.coin
        if coin_cash_proportion <= 0:
            self.update_status(StatusCode.ERROR_UNKNOWN)
            raise
        if current_coin < coin:
            self.update_status(StatusCode.ERROR_DATA)
            self.message = '金币不足'
            raise ValidationError('金币不足')
        cash = round(coin / float(coin_cash_proportion) * 100, 0)
        self.user.cash += cash
        self.user.coin -= coin
        self.user.save()
        return cash

    @transaction.atomic()
    def form_valid(self, form):
        try:
            super(CreateExchangeRecordView, self).form_valid(form)
            cash = self.exchange_cash(form.cleaned_data.get('coin', 0))
            exchange_record = form.save()
            exchange_record.belong = self.user
            exchange_record.cash = cash
            exchange_record.proportion = self.conf.get('coin_cash_proportion', 1000)
            exchange_record.save()
            return self.render_to_response(dict())
        except Exception as e:
            return self.render_to_response({})


class RewardView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    model = RedPacket
    http_method_names = ['post']
    conf = {}

    def get_reward(self):
        reward_list = []
        amount = 0
        if self.user.cash >= DEFAULT_MAX_CASH_LIMIT:
            amount = random.randint(1, 2)
        else:
            amount = random.randint(20, 500)
        rp = RedPacket()
        rp.amount = amount
        rp.status = STATUS_USED
        rp.reward_type = PACKET_TYPE_CASH
        rp.belong = self.user
        rp.save()
        self.user.cash += amount
        self.user.save()
        reward = {'reward_type': PACKET_TYPE_CASH, 'amount': amount, 'hit': True}
        reward_list.append(reward)
        reward1 = random.randint(PACKET_TYPE_CASH, PACKET_TYPE_WITHDRAW)
        reward2 = random.randint(PACKET_TYPE_CASH, PACKET_TYPE_WITHDRAW)
        if reward1 == PACKET_TYPE_CASH:
            reward_list.append({'reward_type': PACKET_TYPE_CASH, 'amount': amount, 'hit': False})
        else:
            reward_list.append({'reward_type': reward1, 'amount': 1, 'hit': False})
        if reward2 == PACKET_TYPE_CASH:
            reward_list.append({'reward_type': PACKET_TYPE_CASH, 'amount': amount, 'hit': False})
        else:
            reward_list.append({'reward_type': reward2, 'amount': 1, 'hit': False})
        return reward_list

    def get_new_reward(self):
        conf = get_global_conf()
        new_packet = int(conf.get('new_red_packet', DEFAULT_NEW_PACKET))
        self.user.cash += new_packet
        self.user.new_red_packet = True
        return True

    def post(self, request, *args, **kwargs):
        new_packet = int(request.POST.get('new_packet', 0))
        if new_packet:
            if self.user.new_red_packet:
                self.update_status(StatusCode.ERROR_REPEAT_NEW_PACKET)
                return self.render_to_response()
            self.get_new_reward()
            self.user.save()
            return self.render_to_response()
        if not client_redis_riddle.delete(REWARD_KEY.format(self.user.id)):
            self.update_status(StatusCode.ERROR_REWARD_DENIED)
            return self.render_to_response()
        reward_list = self.get_reward()
        return self.render_to_response({'reward_list': reward_list})
