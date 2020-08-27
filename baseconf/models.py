# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel

# Create your models here.
from core.cache import set_global_config_to_cache
from core.dss.Serializer import serializer


class GlobalConf(BaseModel):
    coin_cash_proportion = models.IntegerField(default=1000)
    total_level = models.IntegerField(default=800)
    round_coin = models.IntegerField(default=3000)
    round_count = models.IntegerField(default=50)
    low_range = models.FloatField(default=0.5)
    high_range = models.FloatField(default=1.5)
    const_num = models.IntegerField(default=0)

    def __unicode__(self):
        return '{0}'.format(self.create_time)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        global_conf = serializer(self, output_type='json', exclude_attr=['create_time', 'modify_time'])
        set_global_config_to_cache(global_conf)
        return super(GlobalConf, self).save(force_insert=False, force_update=False, using=None,
                                            update_fields=None)
