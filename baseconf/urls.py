# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from baseconf.views import *

urlpatterns = [
    url(r'^global_conf/$', GlobalConfView.as_view()),
]
