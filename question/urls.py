# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import include, url
from question.views import *

urlpatterns = [
    url(r'^$', FetchQuestionView.as_view()),
    url(r'^(?P<qid>(\w)+)/answer/$', AnswerView.as_view()),
    url(r'^(?P<qid>(\w)+)/stimulate/$', StimulateView.as_view()),
]
