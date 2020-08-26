# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel, User


# Create your models here.


class CashRecord(BaseModel):
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
