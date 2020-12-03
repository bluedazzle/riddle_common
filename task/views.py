# coding: utf-8
import json

from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from baseconf.models import TaskConf
from core.Mixin.StatusWrapMixin import StatusWrapMixin, StatusCode
from core.cache import get_daily_task_config_from_cache, set_daily_task_config_to_cache, \
    get_common_task_config_from_cache, set_common_task_config_to_cache, search_task_id
from core.consts import TASK_OK, TASK_DOING
from core.dss.Mixin import CheckTokenMixin, JsonResponseMixin
from task.utils import create_task


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

    def get(self, request, *args, **kwargs):
        self.get_daily_task_config()
        daily_task_list = []
        task_ok = 0
        for task in self.task_config:
            target = getattr(self.user, task.get("target"))
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

    def get(self, request, *args, **kwargs):
        self.get_common_task_config()
        common_task_list = list()
        task_ok = 0
        for task in self.task_config:
            target = getattr(self.user, task.get("target"))
            for itm in task.get("detail"):
                task = create_task(self.user.id, target, task.get("slug"), **itm)
                if task.get("status") == TASK_OK:
                    task_ok += 1
                common_task_list.append(task)
        common_task_list.sort(key=lambda x: x.get("status"))
        return self.render_to_response({"common_task": common_task_list, 'task_ok_count': task_ok})


class FinishTaskView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):

    def valid_task(self, slug, task_id):
        if search_task_id(task_id):
            self.update_status(StatusCode.ERROR_TASK_FINISHED)

    def send_reward(self):
        pass

    def create_task_history(self):
        pass

    def post(self, request, *args, **kwargs):
        task_id = request.POST.get("task_id")
        slug = request.POST.get('slug')
        self.valid_task(slug, task_id)
        self.send_reward()
        return self.render_to_response({})
