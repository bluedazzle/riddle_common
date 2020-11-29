# coding: utf-8
import hashlib
import json

from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.consts import TASK_OK, TASK_DOING
from core.dss.Mixin import CheckTokenMixin, JsonResponseMixin


class DailyTaskListView(CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    def create_task(self, target, task_slug, *args, **kwargs):
        task = {'current_level': target}
        task.update(kwargs)
        unique_str = ','.join([self.user.id, task_slug, kwargs.get("level"), kwargs.get("reward")])
        task_id = hashlib.md5(unique_str).hexdigest()
        task['id'] = task_id
        task['slug'] = task_slug
        status = TASK_DOING
        if target == kwargs.get("level"):
            status = TASK_OK
        # todo check task if finished
        task['status'] = status
        return task

    def get(self, request, *args, **kwargs):
        daily_task_conf = json.loads('''[
  {"slug": "TASK_GUSS_RIGHT",
    "type": "REPEAT", // REPEAT,ACTION,
    "target": "daily_right_count",
    "detail": [
      {"level": 5, "reward": 2000, "reward_type": "COIN"},
      {"level": 10, "reward": 3000, "reward_type": "COIN"},
      {"level": 30, "reward": 5000, "reward_type": "COIN"},
      {"level": 60, "reward": 10000, "reward_type": "COIN"}
    ]
  },
  {"slug": "TASK_WITHDRAW",
    "type": "ACTION", // REPEAT,ACTION
    "target": "daily_withdraw",
    "detail": [
      {"level": true, "reward": 5000, "reward_type": "COIN"}
    ]
  }
]''')
        daily_task_list = []
        for task in daily_task_conf:
            target = getattr(self.user, task.get("target"))
            for itm in task.get("detail"):
                task = self.create_task(target, task.get("slug"), **itm)
                daily_task_list.append(task)
        return self.render_to_response({"daily_task": daily_task_list})

