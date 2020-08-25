# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils import timezone


# Create your models here.


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    name = models.CharField(max_length=100, default='')
    token = models.CharField(max_length=128, unique=True)
    avatar = models.CharField(max_length=128, default='')
    coin = models.IntegerField(default=0)
    cash = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    device_id = models.CharField(max_length=128, default='', null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    wx_open_id = models.CharField(max_length=128, default='', null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.name)
