# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from account.views import *

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view()),
]
