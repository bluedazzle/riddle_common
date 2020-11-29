# coding: utf-8

from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.dss.Mixin import CheckTokenMixin, JsonResponseMixin


class DailyTaskListView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    def get(self, request, *args, **kwargs):
        conf = '{}'
        pass