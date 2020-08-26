# coding: utf-8
from __future__ import unicode_literals

import random
import string

from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin
from account.models import User


class UserInfoView(CheckTokenMixin, StatusWrapMixin, MultipleJsonResponseMixin, DetailView):
    model = User
    slug_field = 'token'

    # exclude_attr = ['']

    def get(self, request, *args, **kwargs):
        self.kwargs['slug'] = self.token
        return super(UserInfoView, self).get(self, request, *args, **kwargs)


class UserRegisterView(StatusWrapMixin, FormJsonResponseMixin, CreateView):
    model = User
    count = 32

    def post(self, request, *args, **kwargs):
        device_id = request.POST.get('device_id', '')
        user = User()
        user.device_id = device_id
        user.token = self.create_token()
        user.name = self.create_name()
        user.save()
        return self.render_to_response(user)

    def create_name(self):
        name = '游客' + string.join(random.sample('1234567890', 7)).replace(" ", "")
        return name

    def create_token(self):
        token = string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        return token
