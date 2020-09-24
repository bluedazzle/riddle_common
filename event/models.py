# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from account.models import BaseModel


class AdEvent(BaseModel):
    ad_type = models.CharField(max_length=9999)
    extra = models.CharField(max_length=1024, null=True, blank=True)
    user_id = models.IntegerField(default=0)

    def __unicode__(self):
        return '{0}-{1}'.format(self.user_id, self.ad_type)
