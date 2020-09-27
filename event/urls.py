# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from event.views import *

urlpatterns = [
    url(r'^ad/$', CreateAdEventView.as_view()),
]
