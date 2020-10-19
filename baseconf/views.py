# coding: utf-8
from __future__ import unicode_literals

# Create your views here.

from django.views.generic import DetailView, ListView

from core.Mixin.ABTestMixin import ABTestMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.consts import NEW_WITHDRAW, NORMAL_WITHDRAW
from core.dss.Mixin import MultipleJsonResponseMixin, JsonResponseMixin, CheckTokenMixin
from baseconf.models import GlobalConf, PageConf, WithdrawConf
from core.utils import get_global_conf


class GlobalConfView(StatusWrapMixin, JsonResponseMixin, DetailView):
    model = GlobalConf
    slug_field = 'token'

    exclude_attr = ['allow_cash_right_number']

    def get(self, request, *args, **kwargs):
        conf = get_global_conf()
        return self.render_to_response(conf)


class PageConfView(StatusWrapMixin, JsonResponseMixin, DetailView):
    model = PageConf

    def get_object(self, queryset=None):
        return self.model.objects.all()[0]


class WithdrawConfView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = WithdrawConf

    def get(self, request, *args, **kwargs):
        obj = self.model.objects.all()[0]
        obj_list = []
        data = {'available': False if self.user.new_withdraw else True, 'type': NEW_WITHDRAW,
                'amount': obj.new_withdraw_threshold, 'order_id': 0}
        obj_list.append(data)
        data = {'available': False if self.user.cash < obj.withdraw_first_threshold else True, 'type': NORMAL_WITHDRAW,
                'amount': obj.withdraw_first_threshold, 'order_id': 1}
        obj_list.append(data)
        data = {'available': False if self.user.cash < obj.withdraw_second_threshold else True, 'type': NORMAL_WITHDRAW,
                'amount': obj.withdraw_second_threshold, 'order_id': 2}
        obj_list.append(data)
        data = {'available': False if self.user.cash < obj.withdraw_third_threshold else True, 'type': NORMAL_WITHDRAW,
                'amount': obj.withdraw_third_threshold, 'order_id': 3}
        obj_list.append(data)
        return self.render_to_response({'withdraw_conf': obj_list})


class ABTestDemoView(CheckTokenMixin, ABTestMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    def handler_default(self, *args, **kwargs):
        return 'default group'

    def handler_b(self, *args, **kwargs):
        return 'experiment group'

    def get(self, request, *args, **kwargs):
        c_start = self.user.create_time.replace(second=0, microsecond=0)
        c_end = self.user.create_time.replace(second=59, microsecond=999999)
        print(c_start,c_end)
        from account.models import User
        objs = User.objects.filter(create_time__range=(c_start, c_end)).all()
        count = objs.count()
        print(count)
        result = self.ab_test_handle(slug='test1')
        return self.render_to_response({'result': result})
