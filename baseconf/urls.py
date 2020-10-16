# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from baseconf.views import *

urlpatterns = [
    url(r'^global_conf/$', GlobalConfView.as_view()),
    url(r'^page_conf/$', PageConfView.as_view()),
    url(r'^withdraw_conf/$', WithdrawConfView.as_view()),
    url(r'^ab_demo/$', ABTestDemoView.as_view()),
]
