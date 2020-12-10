# coding: utf-8
import hashlib
import json

import datetime
import random

from django.db.models import BooleanField
from django.utils import timezone

from account.models import User
from core.cache import search_task_id_by_cache
from core.consts import TASK_DOING, TASK_OK, TASK_FINISH, TASK_TYPE_DAILY, TASK_TYPE_COMMON
from task.models import DailyTask, CommonTask


def create_task(user: User, target, task_slug: str, title_template, *args, **kwargs):
    task_slug = task_slug.upper()
    task = {'current_level': target}
    task.update(kwargs)
    if task_slug == 'DAILY_TASK_SIGN':
        if not user.daily_sign_in_token:
            user.daily_sign_in_token = create_token()
        sign_token = user.daily_sign_in_token
        unique_str = ','.join(
            [str(user.id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward")), str(sign_token)])
    elif task_slug.startswith('DAILY_'):
        date = datetime.date.today()
        unique_str = ','.join([str(user.id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward")), str(date)])
    else:
        unique_str = ','.join([str(user.id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward"))])
    task_id = hashlib.md5(unique_str.encode(encoding='UTF-8')).hexdigest()
    task['id'] = task_id
    task['title'] = title_template.format(kwargs.get("level"))
    task['slug'] = task_slug
    task['reward'] = kwargs.get("reward")
    task['reward_type'] = kwargs.get("reward_type")
    status = TASK_DOING
    if target >= kwargs.get("level"):
        status = TASK_OK
    if search_task_id_by_cache(task_id):
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


def daily_task_attr_reset(user: User):
    now_time = timezone.localtime()
    if user.daily_reward_modify.astimezone().day != now_time.day:
        user.daily_reward_expire = None
        user.daily_reward_draw = False
        user.daily_reward_stage = 20
        user.daily_reward_count = 0
        user.daily_right_count = 0
        user.daily_watch_ad = 0
        user.daily_reward_modify = now_time
        user.daily_coin_exchange = False
        user.daily_lucky_draw = False
        user.daily_withdraw = False
        if user.daily_sign_in == 7:
            user.daily_sign_in = 0
            user.daily_sign_in_token = create_token()
        user.daily_sign_in += 1
    if user.daily_reward_expire:
        if now_time > user.daily_reward_expire:
            user.daily_reward_draw = False
    return user


def update_task_attr(user: User, attr: str):
    old_value = getattr(user, attr)
    new_value = None
    if isinstance(old_value, int):
        new_value = old_value + 1
    if isinstance(old_value, bool):
        new_value = True
    if new_value:
        setattr(user, attr, new_value)
    return user


def create_token(count=32):
    count = 62 if count > 62 else count
    token = ''.join(
        random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                      count)).replace(" ", "")
    return token
