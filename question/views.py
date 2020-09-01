# coding: utf-8
from __future__ import unicode_literals
import random
import string

# Create your views here.
from django.core.exceptions import ValidationError
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.db import transaction

from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from core.utils import get_global_conf
from core.cache import client_redis_riddle
from question.models import Question


class FetchQuestionView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    exclude_attr = ['wrong_answer_id', 'wrong_answer', 'right_answer', 'right_answer_id']
    pk_url_kwarg = 'qid'

    def get_object(self, queryset=None):
        obj = None
        if self.kwargs.get(self.pk_url_kwarg, None):
            obj = super(FetchQuestionView, self).get_object(queryset)
        else:
            current_level = self.user.current_level
            objs = self.model.objects.filter(order_id=current_level).all()
            if objs.exists():
                obj = objs[0]
        if not obj:
            return obj
        if random.random() > 0.5:
            answer_list = [{'answer_id': obj.wrong_answer_id, 'answer': obj.wrong_answer},
                           {'answer_id': obj.right_answer_id, 'answer': obj.right_answer}]
        else:
            answer_list = [{'answer_id': obj.right_answer_id, 'answer': obj.right_answer},
                           {'answer_id': obj.wrong_answer_id, 'answer': obj.wrong_answer}]
        setattr(obj, 'answer_list', answer_list)
        return obj


class AnswerView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'
    count = 32
    conf = get_global_conf()
    round_coin = conf.get('round_coin', 3000)
    round_count = conf.get('round_count', 50)
    low_range = conf.get('low_range', 0.5)
    high_range = conf.get('high_range', 1.5)
    const_num = conf.get('const_num', 0)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        aid = int(request.GET.get('answer', 0))
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        tag = string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        client_redis_riddle.set(str(self.user.id) + 'tag', tag)
        rand_num = random.random() * (self.high_range - self.low_range) + self.low_range
        coin = int(((2 * self.round_coin / self.round_count) -
                    self.user.current_step * (2 * self.round_coin / self.round_count) / self.round_count)
                   * rand_num + self.const_num)
        if self.user.current_step == self.round_count and self.user.coin < self.round_coin:
            coin = self.round_coin - self.user.coin
        client_redis_riddle.set(str(self.user.id) + 'coin', coin)
        if obj.right_answer_id != aid:
            return self.render_to_response({'answer': False, 'coin': 0})
        if self.user.current_step == self.round_count:
            self.user.current_step = 0
        self.user.current_step += 1
        self.user.coin += coin
        self.user.save()
        return self.render_to_response({'answer': True, 'coin': coin})


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # todo 只是简单让关卡继续，没有做积分逻辑
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        tag = request.GET.get('tag', '0')
        if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
            self.update_status(StatusCode.ERROR_STIMULATE_TAG)
            return self.render_to_response()
        client_redis_riddle.delete(str(self.user.id) + 'tag')
        client_redis_riddle.delete(str(self.user.id) + 'coin')
        if self.user.current_level == 4:
            self.user.current_level = 0
        self.user.current_level += 1
        self.user.save()
        return self.render_to_response()


class WatchVideoView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        tag = request.GET.get('tag', '0')
        if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
            self.update_status(StatusCode.ERROR_STIMULATE_TAG)
            return self.render_to_response()
        coin = request.GET.get('coin', 0)
        self.user.coin += coin
        client_redis_riddle.delete(str(self.user.id) + 'tag')
        client_redis_riddle.delete(str(self.user.id) + 'coin')
        if self.user.current_level == 4:
            self.user.current_level = 0
        self.user.current_level += 1
        self.user.save()
        return self.render_to_response(isValid=True)
