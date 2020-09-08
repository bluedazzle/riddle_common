# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils import timezone


# Create your models here.
from core.consts import NEW_EXTEND_TIMES


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    name = models.CharField(max_length=100, default='')
    token = models.CharField(max_length=128, unique=True)
    avatar = models.CharField(max_length=256, default='')
    province = models.CharField(max_length=30, default='', null=True, blank=True)
    city = models.CharField(max_length=30, default='', null=True, blank=True)
    sex = models.IntegerField(default=3)
    coin = models.IntegerField(default=0)
    cash = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    current_step = models.IntegerField(default=1)
    new_withdraw = models.BooleanField(default=False)
    new_red_packet = models.BooleanField(default=False)
    cash_extend_times = models.IntegerField(default=NEW_EXTEND_TIMES)
    expire_time = models.DateTimeField(default=timezone.now)
    reward_count = models.IntegerField(default=0)
    right_count = models.IntegerField(default=0)
    wrong_count = models.IntegerField(default=0)
    songs_count = models.IntegerField(default=0)
    device_id = models.CharField(max_length=128, default='', null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    wx_open_id = models.CharField(max_length=128, default='', null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.name)
