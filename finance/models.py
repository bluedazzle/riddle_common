# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel, User


# Create your models here.
from core.consts import PACKET_TYPE_NEW_CASH, PACKET_TYPE_CASH, PACKET_TYPE_EXTEND, PACKET_TYPE_PHONE, \
    PACKET_TYPE_WITHDRAW, STATUS_FAIL, STATUS_REVIEW, STATUS_FINISH


class CashRecord(BaseModel):
    status_choices = (
        (STATUS_FAIL, '提现失败'),
        (STATUS_REVIEW, '提现中'),
        (STATUS_FINISH, '提现完成'),
    )

    trade_no = models.CharField(max_length=128, unique=True, default='')
    cash = models.IntegerField()
    status = models.IntegerField(default=STATUS_REVIEW, choices=status_choices)
    reason = models.CharField(max_length=128, default='')
    belong = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return '{0} 提现 {1} 状态: {2} 时间: {3}'.format(self.belong.name, self.cash, self.status, self.create_time)

    def __str__(self):
        return '{0} 提现 {1} 状态: {2} 时间: {3}'.format(self.belong.name, self.cash, self.status, self.create_time)


class ExchangeRecord(BaseModel):
    coin = models.IntegerField()
    cash = models.IntegerField()
    proportion = models.IntegerField(default=0)
    belong = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.coin)

    def __str__(self):
        return '{0}'.format(self.coin)


class RedPacket(BaseModel):
    type_choices = (
        (PACKET_TYPE_NEW_CASH, '新人红包'),
        (PACKET_TYPE_CASH, '现金红包'),
        (PACKET_TYPE_EXTEND, '延时卡'),
        (PACKET_TYPE_PHONE, '手机'),
        (PACKET_TYPE_WITHDRAW, '提现机会'),
    )

    amount = models.IntegerField(default=0)
    reward_type = models.IntegerField(default=PACKET_TYPE_CASH, choices=type_choices)
    status = models.IntegerField(default=0)
    belong = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return '{0}-{1} {2}'.format(self.belong.name, self.amount, self.create_time)

    def __str__(self):
        return '{0}-{1} {2}'.format(self.belong.name, self.amount, self.create_time)
