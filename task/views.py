# coding: utf-8
import json

import logging
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from baseconf.models import TaskConf
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.cache import get_daily_task_config_from_cache, set_daily_task_config_to_cache, \
    get_common_task_config_from_cache, set_common_task_config_to_cache, search_task_id
from core.consts import TASK_OK, TASK_DOING, TASK_TYPE_DAILY, TASK_TYPE_COMMON
from core.dss.Mixin import CheckTokenMixin, JsonResponseMixin
from task.utils import create_task, create_task_history, send_reward


class DailyTaskListView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    task_config = None
    model = TaskConf

    def get_daily_task_config(self):
        conf = get_daily_task_config_from_cache()
        if not conf:
            obj = self.model.objects.all()[0]
            conf = obj.daily_task_config
            set_daily_task_config_to_cache(conf)
            conf = json.loads(conf)
        self.task_config = conf

    @staticmethod
    def format_target(target):
        if isinstance(target, bool):
            return 1 if target else 0
        return target

    def get(self, request, *args, **kwargs):
        self.get_daily_task_config()
        daily_task_list = []
        task_ok = 0
        for task in self.task_config:
            target = self.format_target(getattr(self.user, task.get("target")))
            title = task.get("title")
            for itm in task.get("detail"):
                task = create_task(self.user.id, target, task.get("slug"), title, **itm)
                if task.get("status") == TASK_OK:
                    task_ok += 1
                daily_task_list.append(task)
        daily_task_list.sort(key=lambda x: x.get("status"))
        return self.render_to_response({"daily_task": daily_task_list, 'task_ok_count': task_ok})


class CommonTaskListView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    task_config = None
    model = TaskConf

    def get_common_task_config(self):
        conf = get_common_task_config_from_cache()
        if not conf:
            obj = self.model.objects.all()[0]
            conf = obj.common_task_config
            set_common_task_config_to_cache(conf)
            conf = json.loads(conf)
        self.task_config = conf

    @staticmethod
    def format_target(target):
        if isinstance(target, bool):
            return 1 if target else 0
        return target

    def get(self, request, *args, **kwargs):
        self.get_common_task_config()
        common_task_list = list()
        task_ok = 0
        for task in self.task_config:
            target = self.format_target(getattr(self.user, task.get("target")))
            title = task.get("title")
            for itm in task.get("detail"):
                task = create_task(self.user.id, target, task.get("slug"), title, **itm)
                if task.get("status") == TASK_OK:
                    task_ok += 1
                common_task_list.append(task)
        common_task_list.sort(key=lambda x: x.get("status"))
        return self.render_to_response({"common_task": common_task_list, 'task_ok_count': task_ok})


class FinishTaskView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    task_type = TASK_TYPE_DAILY

    def valid_task(self, slug, task_id):
        if search_task_id(task_id):
            self.update_status(StatusCode.ERROR_TASK_FINISHED)

    def get_task_type(self, slug):
        task_type_dict = {'DAILY': TASK_TYPE_DAILY, 'COMMON': TASK_TYPE_COMMON}
        task_type, others = slug.split('_')
        task_type = task_type.upper()
        self.task_type = task_type_dict.get(task_type, TASK_TYPE_DAILY)

    def get_task_config(self):
        def get_common_task_config():
            conf = get_common_task_config_from_cache()
            if not conf:
                obj = TaskConf.objects.all()[0]
                conf = obj.common_task_config
                set_common_task_config_to_cache(conf)
                conf = json.loads(conf)
            return conf

        def get_daily_task_config():
            conf = get_daily_task_config_from_cache()
            if not conf:
                obj = TaskConf.objects.all()[0]
                conf = obj.daily_task_config
                set_daily_task_config_to_cache(conf)
                conf = json.loads(conf)
            return conf

        config_dict = {TASK_TYPE_DAILY: get_daily_task_config, TASK_TYPE_COMMON: get_common_task_config}
        conf_func = config_dict.get(self.task_type, get_daily_task_config)
        conf = conf_func()
        return conf

    def get_task_dict(self):
        task_dict = {}
        conf = self.get_task_config()
        for task in conf:
            title = task.get("title")
            for itm in task.get("detail"):
                task = create_task(self.user.id, 0, task.get("slug"), title, **itm)
                task_dict[task.get('id')] = task
        return task_dict

    def send_reward(self, task_id):
        task_dict = self.get_task_dict()
        task = task_dict.get(task_id)
        if not task:
            self.update_status()
            raise ValueError('任务不存在')
        reward = task.get('reward')
        reward_type = task.get('reward_type')
        user = send_reward(self.user, reward, reward_type)
        user.save()
        return reward, reward_type

    def create_task_history(self, task_id, slug, **kwargs):
        history = create_task_history(task_id, self.user.id, slug, self.task_type, **kwargs)
        history.save()
        return history

    def post(self, request, *args, **kwargs):
        try:
            task_id = request.POST.get("task_id")
            slug = request.POST.get('slug')
            self.valid_task(slug, task_id)
            self.get_task_type(slug)
            amount, reward_type = self.send_reward(task_id)
            self.create_task_history(task_id, slug)
            return self.render_to_response(
                {"coin": self.user.coin, "cash": self.user.cash, 'amount': amount, 'reward_type': reward_type})
        except Exception as e:
            logging.exception(e)
            return self.render_to_response(e=e)
