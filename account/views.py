# coding: utf-8
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView

from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin
from account.models import User


class UserInfoView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, DetailView):
    model = User
    slug_field = 'token'
    include_attr = ['name', 'token', 'avatar']

    # exclude_attr = ['']

    def get(self, request, *args, **kwargs):
        self.kwargs['slug'] = self.token
        return super(UserInfoView, self).get(self, request, *args, **kwargs)
