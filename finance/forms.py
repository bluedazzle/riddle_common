# coding: utf-8
from __future__ import unicode_literals

from django import forms

from finance.models import CashRecord, ExchangeRecord


class CashRecordForm(forms.ModelForm):
    cash_messages = {
        'not_enough': '提现金额不足',
        'required': '请输入提现金额',
        'max_value': '单次提现金额超过限制',
        'min_value': '提现金额不能为0',
    }

    cash = forms.IntegerField(required=True, min_value=1, max_value=9999999, error_messages=cash_messages)

    def save(self, commit=False):
        return super(CashRecordForm, self).save(commit)

    class Meta:
        model = CashRecord
        fields = ['cash']


class ExchangeRecordForm(forms.ModelForm):
    coin_messages = {
        'not_enough': '兑换金币不足',
        'required': '请输入兑换金额',
        'max_value': '单次兑换金额超过限制',
        'min_value': '兑换金额不能为0',
    }

    coin = forms.IntegerField(required=True, min_value=1, max_value=9999999, error_messages=coin_messages)

    def save(self, commit=False):
        return super(ExchangeRecordForm, self).save(commit)

    class Meta:
        model = ExchangeRecord
        fields = ['coin']
