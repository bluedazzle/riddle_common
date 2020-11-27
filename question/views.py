# coding: utf-8
from __future__ import unicode_literals
import random
import string
import json
import math

# Create your views here.
import logging
from django.http import JsonResponse
from django.views.generic import DetailView

from baseconf.models import PageConf
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.consts import DEFAULT_REWARD_COUNT, DEFAULT_SONGS_COUNT, DEFAULT_SONGS_THRESHOLD, DEFAULT_SONGS_TWO_COUNT, DEFAULT_SONGS_TWO_THRESHOLD, DEFAULT_SONGS_THREE_COUNT, DEFAULT_SONGS_THREE_THRESHOLD, \
    NEW_VERSION_REWARD_COUNT
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
        cash = int(max((kwargs.get('round_cash') - self.user.cash) / (kwargs.get('round_count') - self.user.current_step) * (
                    20 - 19 * self.user.current_step / kwargs.get('round_count')) * kwargs.get('rand_num'), 1))
        return cash

    def handler_b(self, *args, **kwargs):
        cash = int(max((29800 - self.user.cash) / (1000 - self.user.current_step) * (
                17 - 16 * self.user.current_step / 1000) * kwargs.get('rand_num'), 1))
        return cash

    def new_version_handler(self):
       cash_list = [1888, 243, 221, 198, 212, 176, 142, 158, 129, 105]

       if self.user.current_level <= 10:
           cash = cash_list[self.user.current_level - 1]
       else:
           rand_num = random.random() * (120 - 20) + 20
           cash = 50 - (math.floor((self.user.current_level - 10) / 10) * 1) + rand_num
           cash = int(max(cash, 1))

       return cash

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
            # print self.user.current_level, obj.order_id
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        tag = ''.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")
        client_redis_riddle.set(str(self.user.id) + 'tag', tag)

        rand_num = random.random() * (high_range - low_range) + low_range
        # cash = int(((2 * round_cash / round_count) -
        #             self.user.current_step * (2 * round_cash / round_count) / round_count) \
        #            * rand_num + const_num)
        # if cash < 100 and self.user.current_step < 100:
        #     cash = 102
        # if self.user.current_step == round_count and self.user.cash < round_cash:
        #     cash = round_cash - self.user.cash

        # cash = int(max((round_cash-self.user.cash)/(round_count-self.user.current_step)*(20-19*self.user.current_step/round_count)*rand_num, 1))
        # print("round_cash: " + str(round_cash) + " user_cash: " + str(self.user.cash) + " round_count: " + str(round_count) +
        #       " current_step: " + str(self.user.current_step) + " rand_num: " + str(rand_num) + " cash: " + str(cash))
        # if self.user.cash > 29500 and self.user.current_level < 500:
        #     cash = 1

        cash = self.ab_test_handle(slug='2981716', round_cash=round_cash, round_count=round_count, rand_num=rand_num)
        if version >= 20112400 and version <= 20113099:
           cash = self.new_version_handler()

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
        # elif self.user.songs_count > DEFAULT_SONGS_THRESHOLD and \
        #         (self.user.songs_count - DEFAULT_SONGS_THRESHOLD) > DEFAULT_SONGS_COUNT:
        #     self.user.songs_count -= DEFAULT_SONGS_COUNT
        if obj.right_answer_id != aid and self.user.current_level != 1:
            self.user.wrong_count += 1
            self.user.reward_count = 0
            if self.user.current_level == 1185:
                self.user.current_level = 0
            self.user.current_level += 1
            self.user.save()
            return self.render_to_response(
                {'answer': False, 'tag': tag, 'cash': 0, 'reward': False, 'reward_url': '', 'video': video})
        if self.user.current_step == round_count:
            self.user.current_step = 0
        self.user.right_count += 1
        self.user.current_step += 1
        self.user.cash += cash
        self.user.reward_count += 1
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
        if self.user.current_level == 1185:
            self.user.current_level = 0
        self.user.current_level += 1
        self.user.save()
        return self.render_to_response(
            {'answer': True, 'tag': tag, 'cash': cash, 'reward': reward, 'reward_url': reward_url, 'video': video})


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def post(self, request, *args, **kwargs):
        # todo 只是简单让关卡继续，没有做积分逻辑
        # if self.user.current_level - 1 != obj.order_id:
        #     self.update_status(StatusCode.ERROR_QUESTION_ORDER)
        #     return self.render_to_response()
        # tag = request.GET.get('tag', '0')
        # if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
        #     self.update_status(StatusCode.ERROR_STIMULATE_TAG)
        #     return self.render_to_response()
        video = request.GET.get('is_watch_video', '0')
        if video != '1':
            return self.render_to_response()
        cash = client_redis_riddle.get(str(self.user.id) + 'cash')
        if cash:
            try:
                cash = int(cash)
                self.user.cash += cash
                client_redis_riddle.delete(str(self.user.id) + 'tag')
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
        # qid = info['question_id']
        # objs = self.model.objects.filter(id=qid).all()
        # if objs.exists():
        #     obj = objs[0]
        # if not obj:
        #     self.update_status(StatusCode.ERROR_QUESTION_NONE)
        #     return JsonResponse({'isValid': False})
        # if self.user.current_level != obj.order_id:
        #     self.update_status(StatusCode.ERROR_QUESTION_ORDER)
        #     return JsonResponse({'isValid': False})
        # tag = info['tag']
        # if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
        #     self.update_status(StatusCode.ERROR_STIMULATE_TAG)
        #     return JsonResponse({'isValid': False})
        cash = client_redis_riddle.get(str(self.user.id) + 'cash')
        if cash:
            self.user.cash += int(cash)
            client_redis_riddle.delete(str(self.user.id) + 'tag')
            client_redis_riddle.delete(str(self.user.id) + 'cash')
        if self.user.songs_count > 0:
            self.user.songs_count = 0
        # todo 正式上线去掉 or 增加
        self.user.save()
        return JsonResponse({'isValid': True})
