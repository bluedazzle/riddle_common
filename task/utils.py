# coding: utf-8
import hashlib
import json

import datetime

from account.models import User
from core.cache import search_task_id
from core.consts import TASK_DOING, TASK_OK, TASK_FINISH, TASK_TYPE_DAILY, TASK_TYPE_COMMON
from task.models import DailyTask, CommonTask


def create_task(user_id, target, task_slug: str, title_template, *args, **kwargs):
    task_slug = task_slug.upper()
    task = {'current_level': target}
    task.update(kwargs)
    if task_slug.startswith('DAILY_'):
        date = datetime.date.today()
        unique_str = ','.join([str(user_id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward")), str(date)])
    else:
        unique_str = ','.join([str(user_id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward"))])
    task_id = hashlib.md5(unique_str.encode(encoding='UTF-8')).hexdigest()
    task['id'] = task_id
    task['title'] = title_template.format(kwargs.get("level"))
    task['slug'] = task_slug
    task['reward'] = kwargs.get("reward")
    task['reward_type'] = kwargs.get("reward_type")
    status = TASK_DOING
    if target >= kwargs.get("level"):
        status = TASK_OK
    if search_task_id(task_id):
        status = TASK_FINISH
    task['status'] = status
    return task


def create_task_history(task_id, user_id, slug, task_type=TASK_TYPE_DAILY, **kwargs):
    model_dict = {TASK_TYPE_DAILY: DailyTask, TASK_TYPE_COMMON: CommonTask}
    model = model_dict.get(task_type, DailyTask)
    new_history = model()
    detail = json.dumps(kwargs)
    new_history.task_id = task_id
    new_history.belong_id = user_id
    new_history.slug = slug
    new_history.detail = detail
    return new_history


def send_reward(user: User, amount: int, reward_type: str):
    reward_type = reward_type.upper()
    reward_type_dict = {'COIN': 'coin', 'CASH': 'cash'}
    reward_type_attr = reward_type_dict.get(reward_type)
    if not reward_type_attr:
        raise ValueError('奖励类型不存在')
    old_value = getattr(user, reward_type_attr)
    new_value = old_value + amount
    setattr(user, reward_type_attr, new_value)
    return user
