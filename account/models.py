# coding: utf-8

from __future__ import unicode_literals

# import random

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

# Create your models here.
from core.consts import NEW_EXTEND_TIMES


# def create_invite_code():
#     invite_code = ''.join(
#         random.sample('1234567890ZYXWVUTSRQPONMLKJIHGFEDCBAZYXWVUTSRQPONMLKJIHGFEDCBA', 8)).replace(" ", "")
#     return invite_code


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(ExportModelOperationsMixin("User"), BaseModel):
    name = models.CharField(max_length=100, default='', verbose_name='用户名')
    token = models.CharField(max_length=128, unique=True)
    avatar = models.CharField(max_length=256, default='')
    province = models.CharField(max_length=30, default='', null=True, blank=True)
    city = models.CharField(max_length=30, default='', null=True, blank=True, verbose_name='所在城市')
    sex = models.IntegerField(default=3)
    coin = models.IntegerField(default=0)
    cash = models.IntegerField(default=0, verbose_name='现金持有(分)')
    current_level = models.IntegerField(default=1, verbose_name='答题进度')
    current_step = models.IntegerField(default=1)
    new_withdraw = models.BooleanField(default=False, verbose_name='是否进行新人提现')
    new_red_packet = models.BooleanField(default=False, verbose_name='是否领取新人红包')
    cash_extend_times = models.IntegerField(default=NEW_EXTEND_TIMES)
    expire_time = models.DateTimeField(default=timezone.now)
    reward_count = models.IntegerField(default=0)
    continu_count = models.IntegerField(default=0)
    right_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)
    songs_count = models.IntegerField(default=0)
    device_id = models.CharField(max_length=128, default='', null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    wx_open_id = models.CharField(max_length=128, default='', null=True, blank=True)
    # invite_code = models.CharField(max_length=8, default=create_invite_code, verbose_name='邀请码')
    invite_code = models.CharField(max_length=8, default='', null=True, blank=True, verbose_name='邀请码')
    inviter = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    login_bonus = models.BooleanField(default=False, verbose_name='是否领取邀请登录红包')
    songs_bonus = models.BooleanField(default=False, verbose_name='是否领取邀请答题红包')
    check_point_draw = models.BooleanField(default=False)

    ab_test_id = models.CharField(max_length=100, default='')
    valid_register = models.BooleanField(default=False)
    daily_reward_stage = models.IntegerField(default=20)  # 日常任务阶段 20/40/60/80
    daily_reward_draw = models.BooleanField(default=False)  # 是否可以抽取提现机会
    daily_reward_count = models.IntegerField(default=0)  # 当前任务进度
    daily_reward_expire = models.DateTimeField(null=True, blank=True)  # 过期时间
    daily_reward_modify = models.DateTimeField(default=timezone.now)  # 修改时间
    daily_coin_exchange = models.BooleanField(default=False)
    daily_lucky_draw = models.BooleanField(default=False)
    daily_withdraw = models.BooleanField(default=False)
    daily_right_count = models.IntegerField(default=0)
    daily_watch_ad = models.IntegerField(default=0)
    daily_sign_in = models.IntegerField(default=0)
    daily_sign_in_token = models.CharField(max_length=64, default='')

    def __unicode__(self):
        return '{0}'.format(self.name)

    def __str__(self):
        return '{0}'.format(self.name)
