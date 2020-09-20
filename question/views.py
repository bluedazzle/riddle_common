# coding: utf-8
from __future__ import unicode_literals
import random
import string
import json

# Create your views here.
from django.http import JsonResponse
from django.views.generic import DetailView

from baseconf.models import PageConf
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.consts import DEFAULT_REWARD_COUNT, DEFAULT_SONGS_COUNT, DEFAULT_SONGS_THRESHOLD
from core.dss.Mixin import MultipleJsonResponseMixin, CheckTokenMixin, FormJsonResponseMixin, JsonResponseMixin
from core.utils import get_global_conf
from core.cache import client_redis_riddle, REWARD_KEY
from question.models import Question
from account.models import User


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


class AnswerView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'
    count = 32
    conf = {}

    def get(self, request, *args, **kwargs):
        self.conf = get_global_conf()
        round_cash = self.conf.get('round_cash', 30000)
        round_count = self.conf.get('round_count', 700)
        low_range = self.conf.get('low_range', 0.5)
        high_range = self.conf.get('high_range', 1.5)
        const_num = self.conf.get('const_num', 0)
        obj = self.get_object()
        aid = int(request.GET.get('answer', 0))
        if self.user.current_level != obj.order_id:
            # print self.user.current_level, obj.order_id
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        tag = string.join(
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

        cash = int(max((round_cash-self.user.cash)/(round_count-self.user.current_step)*(3-2*self.user.current_step/round_count)*rand_num, 5*rand_num))

        client_redis_riddle.set(str(self.user.id) + 'cash', cash)
        video = False
        self.user.songs_count += 1
        if self.user.songs_count > DEFAULT_SONGS_THRESHOLD and \
                (self.user.songs_count - DEFAULT_SONGS_THRESHOLD) == DEFAULT_SONGS_COUNT:
            video = True
        elif self.user.songs_count > DEFAULT_SONGS_THRESHOLD and \
                (self.user.songs_count - DEFAULT_SONGS_THRESHOLD) > DEFAULT_SONGS_COUNT:
            self.user.songs_count -= DEFAULT_SONGS_COUNT
        if obj.right_answer_id != aid:
            self.user.wrong_count += 1
            self.user.reward_count = 0
            if self.user.current_level == 500:
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
        if self.user.reward_count == DEFAULT_REWARD_COUNT:
            obj = PageConf.objects.all()[0]
            reward = True
            reward_url = obj.rewards_url
            self.user.reward_count = 0
            client_redis_riddle.set(REWARD_KEY.format(self.user.id), 1, 600)
        elif self.user.reward_count > DEFAULT_REWARD_COUNT:
            self.user.reward_count -= DEFAULT_REWARD_COUNT
        if self.user.current_level == 500:
            self.user.current_level = 0
        self.user.current_level += 1
        self.user.save()
        return self.render_to_response(
            {'answer': True, 'tag': tag, 'cash': cash, 'reward': reward, 'reward_url': reward_url, 'video': video})


class StimulateView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Question
    pk_url_kwarg = 'qid'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        # todo 只是简单让关卡继续，没有做积分逻辑
        if self.user.current_level - 1 != obj.order_id:
            self.update_status(StatusCode.ERROR_QUESTION_ORDER)
            return self.render_to_response()
        # tag = request.GET.get('tag', '0')
        # if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
        #     self.update_status(StatusCode.ERROR_STIMULATE_TAG)
        #     return self.render_to_response()
        # client_redis_riddle.delete(str(self.user.id) + 'tag')
        # client_redis_riddle.delete(str(self.user.id) + 'cash')
        # if self.user.current_level == 100:
        #     self.user.current_level = 0
        # self.user.current_level += 1
        # self.user.save()
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
        import urlparse
        resp = urlparse.unquote(data)
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
        qid = info['question_id']
        objs = self.model.objects.filter(id=qid).all()
        if objs.exists():
            obj = objs[0]
        if not obj:
            self.update_status(StatusCode.ERROR_QUESTION_NONE)
            return JsonResponse({'isValid': False})
        # if self.user.current_level != obj.order_id:
        #     self.update_status(StatusCode.ERROR_QUESTION_ORDER)
        #     return JsonResponse({'isValid': False})
        tag = info['tag']
        if tag != client_redis_riddle.get(str(self.user.id) + 'tag'):
            self.update_status(StatusCode.ERROR_STIMULATE_TAG)
            return JsonResponse({'isValid': False})
        cash = client_redis_riddle.get(str(self.user.id) + 'cash')
        self.user.cash += int(cash)
        client_redis_riddle.delete(str(self.user.id) + 'tag')
        client_redis_riddle.delete(str(self.user.id) + 'cash')
        if self.user.songs_count > DEFAULT_SONGS_THRESHOLD:
            self.user.songs_count = DEFAULT_SONGS_THRESHOLD
        # todo 正式上线去掉 or 增加
        self.user.save()
        return JsonResponse({'isValid': True})
