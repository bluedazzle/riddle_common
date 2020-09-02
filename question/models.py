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


class Question(BaseModel):
    title = models.CharField(max_length=100, default='')
    order_id = models.IntegerField(unique=True)
    question_type = models.IntegerField(default=1)
    difficult = models.IntegerField(default=1)
    right_answer_id = models.IntegerField()
    right_answer = models.CharField(max_length=100)
    wrong_answer_id = models.IntegerField()
    wrong_answer = models.CharField(max_length=100)
    resource_url = models.CharField(max_length=256)

    def __unicode__(self):
        return '排序:{0}-{1}:{2}'.format(self.order_id, self.title, self.right_answer)
