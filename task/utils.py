# coding: utf-8
import hashlib

from core.cache import search_task_id
from core.consts import TASK_DOING, TASK_OK, TASK_FINISH


def create_task(user_id, target, task_slug, *args, **kwargs):
    task = {'current_level': target}
    task.update(kwargs)
    unique_str = ','.join([str(user_id), task_slug, str(kwargs.get("level")), str(kwargs.get("reward"))])
    task_id = hashlib.md5(unique_str.encode(encoding='UTF-8')).hexdigest()
    task['id'] = task_id
    task['slug'] = task_slug
    status = TASK_DOING
    if target == kwargs.get("level"):
        status = TASK_OK
    if search_task_id(task_id):
        status = TASK_FINISH
    task['status'] = status
    return task
