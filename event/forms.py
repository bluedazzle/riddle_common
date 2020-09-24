# coding: utf-8
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError

from core.consts import EVENT_AD_STIMULATE_RIGHT, EVENT_AD_STIMULATE_WRONG, EVENT_AD_STIMULATE_FORCE, \
    EVENT_AD_CARD_RESDIA, EVENT_AD_CARD_USERCENTER, EVENT_AD_STIMULATE_FORCE_WRONG, EVENT_AD_STIMULATE_FORCE_RIGHT, \
    EVENT_AD_SPLASH
from event.models import AdEvent


class AdEventForm(forms.ModelForm):
    cash_messages = {
        'required': '广告类型缺失',
        'max_value': '广告类型缺失',
        'min_value': '广告类型缺失',
    }

    ad_type = forms.IntegerField(required=True, min_value=1, max_value=9999999, error_messages=cash_messages)
    extra = forms.CharField(required=False, max_length=1024)

    def clean_ad_type(self):
        ad_type = self.cleaned_data.get('ad_type', 0)
        ad_type_list = [EVENT_AD_STIMULATE_RIGHT, EVENT_AD_STIMULATE_WRONG, EVENT_AD_STIMULATE_FORCE_WRONG,
                        EVENT_AD_STIMULATE_FORCE_RIGHT, EVENT_AD_SPLASH,
                        EVENT_AD_CARD_RESDIA, EVENT_AD_CARD_USERCENTER]
        if ad_type not in ad_type_list:
            raise ValidationError('事件类型不合法')
        return ad_type

    def save(self, commit=False):
        return super(AdEventForm, self).save(commit)

    class Meta:
        model = AdEvent
        fields = ['ad_type']
