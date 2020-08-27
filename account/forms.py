# coding: utf-8
from __future__ import unicode_literals

from django import forms


class VerifyCodeForm(forms.Form):
    phone_messages = {
        'required': '请输入11位手机号码',
        'max_length': '请输入11位手机号码',
        'min_length': '请输入11位手机号码',
    }

    phone = forms.CharField(required=True, max_length=11, min_length=11, error_messages=phone_messages)


class ValidateVerifyCodeForm(forms.Form):
    phone_messages = {
        'required': '请输入11位手机号码',
        'max_length': '请输入11位手机号码',
        'min_length': '请输入11位手机号码',
    }

    code_messages = {
        'required': '请输入4位验证码',
        'max_length': '请输入4位验证码',
        'min_length': '请输入4位验证码',
    }

    phone = forms.CharField(required=True, max_length=11, min_length=11, error_messages=phone_messages)
    code = forms.CharField(required=True, max_length=4, min_length=4, error_messages=code_messages)
