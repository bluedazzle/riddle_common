# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel

# Create your models here.
from core.cache import set_global_config_to_cache
from core.consts import DEFAULT_ALLOW_CASH_COUNT, DEFAULT_COIN_CASH_PROPORTION, TOTAL_LEVEL, ROUND_CASH, ROUND_COUNT, \
    DEFAULT_NEW_PACKET
from core.dss.Serializer import serializer


class GlobalConf(BaseModel):
    coin_cash_proportion = models.IntegerField(default=DEFAULT_COIN_CASH_PROPORTION)
    total_level = models.IntegerField(default=TOTAL_LEVEL)
    round_cash = models.IntegerField(default=ROUND_CASH)
    round_count = models.IntegerField(default=ROUND_COUNT)
    low_range = models.FloatField(default=0.5)
    high_range = models.FloatField(default=1.5)
    const_num = models.IntegerField(default=0)
    new_red_packet = models.IntegerField(default=DEFAULT_NEW_PACKET)
    allow_cash_count = models.IntegerField(default=DEFAULT_ALLOW_CASH_COUNT, verbose_name='提现门槛(单位: 分)')

    def __unicode__(self):
        return '{0}'.format(self.create_time)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        global_conf = serializer(self, output_type='json', exclude_attr=['create_time', 'modify_time'])
        set_global_config_to_cache(global_conf)
        return super(GlobalConf, self).save(force_insert=False, force_update=False, using=None,
                                            update_fields=None)
