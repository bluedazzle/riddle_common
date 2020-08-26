# coding: utf-8
from __future__ import unicode_literals

# Create your views here.
from django.core.exceptions import ValidationError
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.db import transaction

from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from core.utils import get_global_conf
from question.models import Question


class FetchQuestionView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question

    def get_object(self, queryset=None):
        current_level = self.user.current_level
        objs = self.model.objects.filter(order_id=current_level).all()
        if objs.exists():
            return objs[0]


class AnswerView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    pass