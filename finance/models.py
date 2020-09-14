# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel, User


# Create your models here.
from core.consts import PACKET_TYPE_NEW_CASH, PACKET_TYPE_CASH, PACKET_TYPE_EXTEND, PACKET_TYPE_PHONE, \
    PACKET_TYPE_WITHDRAW


class CashRecord(BaseModel):
    trade_no = models.CharField(max_length=128, unique=True, default='')
    cash = models.IntegerField()
    status = models.IntegerField(default=1)
    reason = models.CharField(max_length=128, default='')
    belong = models.ForeignKey(User)

    def __unicode__(self):
        return '{0}'.format(self.cash)


class ExchangeRecord(BaseModel):
    coin = models.IntegerField()
    cash = models.IntegerField()
    proportion = models.IntegerField(default=0)
    belong = models.ForeignKey(User)

    def __unicode__(self):
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
    belong = models.ForeignKey(User)

    def __unicode__(self):
        return self.amount
