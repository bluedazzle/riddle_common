# coding: utf-8
from __future__ import unicode_literals
import random
import string
import json

# Create your views here.
import logging

import datetime
from django.http import JsonResponse
from django.views.generic import DetailView
from django.utils import timezone

from baseconf.models import PageConf
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.consts import DEFAULT_REWARD_COUNT, DEFAULT_SONGS_COUNT, DEFAULT_SONGS_THRESHOLD, DEFAULT_SONGS_TWO_COUNT, \
    DEFAULT_SONGS_TWO_THRESHOLD, DEFAULT_SONGS_THREE_COUNT, DEFAULT_SONGS_THREE_THRESHOLD, \
    NEW_VERSION_REWARD_COUNT, DEFAULT_QUESTION_NUMBER
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from core.utils import get_global_conf
from core.cache import client_redis_riddle, REWARD_KEY
from question.models import Question
from account.models import User
from core.Mixin.ABTestMixin import ABTestMixin


class FetchQuestionView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    exclude_attr = ['wrong_answer_id', 'wrong_answer', 'right_answer', 'right_answer_id']
    pk_url_kwarg = 'qid'
    datetime_type = 'timestamp'

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


class AnswerView(CheckTokenMixin, ABTestMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'
    count = 32
    conf = {}

    def handler_default(self, *args, **kwargs):
        cash = int(
            max((kwargs.get('round_cash') - self.user.cash) / (kwargs.get('round_count') - self.user.current_step) * (
                20 - 19 * self.user.current_step / kwargs.get('round_count')) * kwargs.get('rand_num'), 1)) + kwargs.get('const_num')
        return cash

    def handler_b(self, *args, **kwargs):
        cash = int(max((29800 - self.user.cash) / (1000 - self.user.current_step) * (
                17 - 16 * self.user.current_step / 1000) * kwargs.get('rand_num'), 1)) + kwargs.get('const_num')

        return cash

    def daily_rewards_handler(self):
        now_time = timezone.now()
        if self.user.daily_reward_modify.day != now_time.day:
            self.user.daily_reward_expire = None
            self.user.daily_reward_draw = False
            self.user.daily_reward_stage = 20
            self.user.daily_reward_count = 0
        if self.user.daily_reward_expire:
            if now_time > self.user.daily_reward_expire:
                self.user.daily_reward_draw = False
        self.user.daily_reward_count += 1
        if self.user.daily_reward_count == self.user.daily_reward_stage:
            self.user.daily_reward_draw = True
            self.user.daily_reward_expire = now_time + datetime.timedelta(minutes=10)
            self.user.daily_reward_stage += 20
        self.user.daily_reward_modify = now_time
        return self.user.daily_reward_count

    def get(self, request, *args, **kwargs):
        reward_count = DEFAULT_REWARD_COUNT
        version = int(request.GET.get('version', 0))
        if version >= 20100301:
            reward_count = NEW_VERSION_REWARD_COUNT
        if version >= 20101001:
            reward_count = DEFAULT_REWARD_COUNT

        self.conf = get_global_conf()
        round_cash = self.conf.get('round_cash', 30000)
        round_count = self.conf.get('round_count', 1000)
        low_range = self.conf.get('low_range', 0.8)
        high_range = self.conf.get('high_range', 1.2)
        const_num = self.conf.get('const_num', 0)

        obj = self.get_object()
        aid = int(request.GET.get('answer', 0))
        if self.user.current_level != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()

        rand_num = random.random() * (high_range - low_range) + low_range
        cash = self.ab_test_handle(slug='2981716', round_cash=round_cash, round_count=round_count, rand_num=rand_num, const_num=const_num)
        client_redis_riddle.set(str(self.user.id) + 'cash', cash)

        video = False
        self.user.songs_count += 1
        if self.user.current_level > DEFAULT_SONGS_THRESHOLD and self.user.current_level <= DEFAULT_SONGS_TWO_THRESHOLD and \
                                self.user.songs_count % DEFAULT_SONGS_COUNT == 0:
            video = True
        elif self.user.current_level > DEFAULT_SONGS_TWO_THRESHOLD and self.user.current_level <= DEFAULT_SONGS_THREE_THRESHOLD and \
                                self.user.songs_count % DEFAULT_SONGS_TWO_COUNT == 0:
            video = True
        elif self.user.current_level > DEFAULT_SONGS_THREE_THRESHOLD and \
                                self.user.songs_count % DEFAULT_SONGS_THREE_COUNT == 0:
            video = True

        if obj.right_answer_id != aid:
            self.user.wrong_count += 1
            self.user.reward_count = 0
            if self.user.current_level == DEFAULT_QUESTION_NUMBER:
                self.user.current_level = 0
            self.user.current_level += 1
            self.user.save()
            return self.render_to_response(
                {'answer': False, 'cash': 0, 'reward': False, 'reward_url': '', 'video': video})

        if self.user.current_step == round_count:
            self.user.current_step = 0
        self.user.current_step += 1
        self.user.right_count += 1
        self.user.reward_count += 1
        self.user.cash += cash
        reward = False
        reward_url = ''
        if self.user.reward_count == reward_count:
            obj = PageConf.objects.all()[0]
            reward = True
            reward_url = obj.rewards_url
            self.user.reward_count = 0
            client_redis_riddle.set(REWARD_KEY.format(self.user.id), 1, 600)
        elif self.user.reward_count > reward_count:
            self.user.reward_count -= reward_count
        if self.user.current_level == DEFAULT_QUESTION_NUMBER:
            self.user.current_level = 0
        self.user.current_level += 1
        self.daily_rewards_handler()
        self.user.save()
        return self.render_to_response(
            {'answer': True, 'cash': cash, 'reward': reward, 'reward_url': reward_url, 'video': video})


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def post(self, request, *args, **kwargs):
        video = request.GET.get('is_watch_video', '0')
        if video != '1':
            return self.render_to_response()
        cash = client_redis_riddle.get(str(self.user.id) + 'cash')
        if cash:
            try:
                cash = int(cash)
                self.user.cash += cash
                client_redis_riddle.delete(str(self.user.id) + 'cash')
                self.user.save()
            except Exception as e:
                logging.exception(e)
        return self.render_to_response()


class WatchVideoView(StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question

    def check_token(self, token):
        user_list = User.objects.filter(token=token)
        if user_list.exists():
            self.user = user_list[0]
            return True
        return False

    def check_token_result(self, token):
        result = self.check_token(token)
        if not result:
            self.update_status(StatusCode.ERROR_PERMISSION_DENIED)
            return False
        return True

    def parse_data(self, data):
        import urllib.parse
        resp = urllib.parse.unquote(data)
        return resp

    def get(self, request, *args, **kwargs):
        obj = None
        extra = request.GET.get('extra', '')
        if not extra:
            return JsonResponse({'isValid': False})
        extra = self.parse_data(extra)
        info = json.loads(extra)
        token = info['token']
        if not self.check_token_result(token):
            return JsonResponse({'isValid': False})
        cash = client_redis_riddle.get(str(self.user.id) + 'cash')
        if cash:
            self.user.cash += int(cash)
            client_redis_riddle.delete(str(self.user.id) + 'cash')
        if self.user.songs_count > 0:
            self.user.songs_count = 0
        self.user.save()
        return JsonResponse({'isValid': True})
