# coding: utf-8

from __future__ import unicode_literals
from django.db import models
from account.models import BaseModel


# Create your models here.


class Song(BaseModel):
    name = models.CharField(max_length=100, default='')
    singer = models.CharField(max_length=128, default='')
    resource_url = models.CharField(max_length=128, default='')

    def __unicode__(self):
        return '{0}'.format(self.name)
