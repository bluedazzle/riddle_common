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
    pk_url_kwarg = 'qid'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        aid = int(request.GET.get('answer', 0))
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        # todo 这一步还应该下发一个唯一 id，确保 StimulateView 不被随意调用
        if obj.right_answer_id != aid:
            return self.render_to_response({'answer': False})
        return self.render_to_response({'answer': True})


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # todo 只是简单让关卡继续，没有做积分逻辑
        is_watch = int(request.GET.get('is_watch_video', 0))
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        if self.user.current_level == 4:
            self.user.current_level = 0
        self.user.current_level += 1
        self.user.save()
        return self.render_to_response()
