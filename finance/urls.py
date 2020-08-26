# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from finance.views import *

urlpatterns = [
    url(r'^cash_records/$', CashRecordListView.as_view()),
    url(r'^cash/$', CreateCashRecordView.as_view()),
    url(r'^exchange_records/$', ExchangeRecordListView.as_view()),
    url(r'^exchange/$', CreateExchangeRecordView.as_view()),
]
