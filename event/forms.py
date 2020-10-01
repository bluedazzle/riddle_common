# coding: utf-8
from __future__ import unicode_literals

from django import forms
from event.models import AdEvent


class AdEventForm(forms.ModelForm):
    cash_messages = {
        'required': '广告类型缺失',
        'max_length': '广告类型超过限制',
    }

    ad_type = forms.CharField(required=True, max_length=9999, error_messages=cash_messages)
    channel = forms.CharField(required=False, max_length=1000)
    extra = forms.CharField(required=False, max_length=1024, default='')

    def save(self, commit=False):
        return super(AdEventForm, self).save(commit)

    class Meta:
        model = AdEvent
        fields = ['ad_type', 'channel', 'extra']
