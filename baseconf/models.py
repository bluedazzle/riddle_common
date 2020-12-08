# coding: utf-8

from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from account.models import BaseModel

# Create your models here.
from core.cache import set_global_config_to_cache, update_ab_test_config_from_cache, set_daily_task_config_to_cache, \
    set_common_task_config_to_cache
from core.consts import DEFAULT_ALLOW_CASH_COUNT, DEFAULT_ALLOW_CASH_TWO, DEFAULT_ALLOW_CASH_THREE, DEFAULT_COIN_CASH_PROPORTION, TOTAL_LEVEL, ROUND_CASH, ROUND_COUNT, \
    DEFAULT_NEW_PACKET, DEFAULT_NEW_WITHDRAW_THRESHOLD, DEFAULT_FIRST_WITHDRAW_THRESHOLD, \
    DEFAULT_SECOND_WITHDRAW_THRESHOLD, DEFAULT_THIRD_WITHDRAW_THRESHOLD, DEFAULT_ALLOW_CASH_RIGHT_COUNT, STATUS_FAIL, \
    STATUS_DESTROY, STATUS_FINISH, STATUS_ENABLE, STATUS_PAUSE
from core.dss.Serializer import serializer


class GlobalConf(ExportModelOperationsMixin("GlobalConf"), BaseModel):
    coin_cash_proportion = models.IntegerField(default=DEFAULT_COIN_CASH_PROPORTION)
    total_level = models.IntegerField(default=TOTAL_LEVEL)
    round_cash = models.IntegerField(default=ROUND_CASH)
    round_count = models.IntegerField(default=ROUND_COUNT)
    low_range = models.FloatField(default=0.9)
    high_range = models.FloatField(default=1.0)
    const_num = models.IntegerField(default=0)
    new_red_packet = models.IntegerField(default=DEFAULT_NEW_PACKET)
    allow_cash_count = models.IntegerField(default=DEFAULT_ALLOW_CASH_COUNT, verbose_name='提现金额门槛(单位: 分)')
    allow_cash_two = models.IntegerField(default=DEFAULT_ALLOW_CASH_TWO, verbose_name='提现金额门槛2(单位: 分)')
    allow_cash_three = models.IntegerField(default=DEFAULT_ALLOW_CASH_THREE, verbose_name='提现金额门槛3(单位: 分)')
    allow_cash_right_number = models.IntegerField(default=DEFAULT_ALLOW_CASH_RIGHT_COUNT, verbose_name='提现题目门槛')
    perfect_level = models.IntegerField(default=29897)

    def __unicode__(self):
        return '全局配置'

    def __str__(self):
        return '全局配置'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        global_conf = serializer(self, output_type='json', exclude_attr=['create_time', 'modify_time'])
        set_global_config_to_cache(global_conf)
        return super(GlobalConf, self).save(force_insert=False, force_update=False, using=None,
                                            update_fields=None)


class WithdrawConf(ExportModelOperationsMixin("WithdrawConf"), BaseModel):
    new_withdraw_threshold = models.IntegerField(default=DEFAULT_NEW_WITHDRAW_THRESHOLD)
    withdraw_first_threshold = models.IntegerField(default=DEFAULT_FIRST_WITHDRAW_THRESHOLD)
    withdraw_second_threshold = models.IntegerField(default=DEFAULT_SECOND_WITHDRAW_THRESHOLD)
    withdraw_third_threshold = models.IntegerField(default=DEFAULT_THIRD_WITHDRAW_THRESHOLD)

    def __unicode__(self):
        return '提现配置'

    def __str__(self):
        return '提现配置'


class TaskConf(ExportModelOperationsMixin("TaskConf"), BaseModel):
    daily_task_config = models.TextField(max_length=10000, null=True, blank=True)
    common_task_config = models.TextField(max_length=10000, null=True, blank=True)

    def __unicode__(self):
        return '任务配置'

    def __str__(self):
        return '任务配置'

    def clean(self):
        errors = {}
        try:
            json.loads(self.daily_task_config)
        except ValidationError as e:
            errors['daily_task_config'] = e.error_list
        try:
            json.loads(self.common_task_config)
        except ValidationError as e:
            errors['common_task_config'] = e.error_list
        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        set_daily_task_config_to_cache(self.daily_task_config)
        set_common_task_config_to_cache(self.common_task_config)
        return super(TaskConf, self).save(force_insert, force_update, using, update_fields)


class PageConf(ExportModelOperationsMixin("PageConf"), BaseModel):
    privacy_url = models.URLField(verbose_name='隐私协议', null=True, blank=True)
    user_agreement_url = models.URLField(verbose_name='用户协议', null=True, blank=True)
    rewards_url = models.URLField(verbose_name='抽奖地址', null=True, blank=True)

    def __unicode__(self):
        return '页面地址配置'

    def __str__(self):
        return '页面地址配置'


class ABTest(ExportModelOperationsMixin("ABTest"), BaseModel):
    status_choices = (
        (STATUS_ENABLE, '启用'),
        (STATUS_PAUSE, '暂停'),
        (STATUS_DESTROY, '终止'),
    )
    name = models.CharField(verbose_name='实验名称', default='实验组', max_length=100)
    slug = models.CharField(verbose_name='实验标识符（唯一）', default='', max_length=10)
    desc = models.TextField(verbose_name='实验描述', default='实验描述', null=True, blank=True, max_length=4096)
    status = models.IntegerField(verbose_name='实验状态', default=STATUS_ENABLE, choices=status_choices)
    # 11~110
    traffic = models.IntegerField(verbose_name='本组实验共占用的流量百分比，实验对照组将均分此占比，请输入2~100的偶数)', default=10)
    test_a_id = models.IntegerField(default=1, editable=False)
    test_a_start_value = models.IntegerField(default=0, editable=False)
    test_a_end_value = models.IntegerField(default=0, editable=False)
    test_b_id = models.IntegerField(default=2, editable=False)
    test_b_start_value = models.IntegerField(default=0, editable=False)
    test_b_end_value = models.IntegerField(default=0, editable=False)

    def clean(self):
        errors = {}
        obj = ABTest.objects.filter(id=self.id).all()
        if not obj.exists():
            try:
                if self.traffic > 100:
                    raise ValidationError("实验流量占比不能 > 100%")
                if self.traffic % 2 == 1:
                    raise ValidationError("实验流量无法均分")
                objs = ABTest.objects.exclude(status=STATUS_DESTROY).order_by('-create_time').all()
                cursor = 0
                if objs.exists():
                    ob = objs[0]
                    cursor = ob.test_b_end_value + 1
                if cursor + self.traffic > 99:
                    raise ValidationError('剩余实验流量不足新建本实验')
            except ValidationError as e:
                errors['traffic'] = e.error_list
        else:
            ext = obj[0]
            try:
                if self.traffic != ext.traffic:
                    raise ValidationError('流量占比无法修改')
            except ValidationError as e:
                errors['traffic'] = e.error_list
        try:
            if obj.exists():
                ext = obj[0]
                if ext.status == STATUS_DESTROY and self.status != STATUS_DESTROY:
                    raise ValidationError('已终止实验无法开启')
        except ValidationError as e:
            errors['status'] = e.error_list
        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        obj = ABTest.objects.filter(id=self.id).all()
        if obj.exists():
            return super(ABTest, self).save(force_insert=False, force_update=False, using=None,
                                            update_fields=None)
        objs = ABTest.objects.exclude(status=STATUS_DESTROY).order_by('-create_time').all()
        cursor = 0
        if objs.exists():
            obj = objs[0]
            cursor = obj.test_b_end_value + 1
        step = self.traffic / 2 - 1
        self.test_a_start_value = cursor
        cursor += step
        self.test_a_end_value = cursor
        cursor += 1
        self.test_b_start_value = cursor
        cursor += step
        self.test_b_end_value = cursor
        ret = super(ABTest, self).save(force_insert=False, force_update=False, using=None,
                                       update_fields=None)
        update_ab_test_config_from_cache()
        return ret

    def __str__(self):
        return self.name
