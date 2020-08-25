# coding: utf-8
from __future__ import unicode_literals

import redis

client_redis_riddle = None


def config_client_redis_zhz():
    global client_redis_riddle
    client_redis_riddle = redis.StrictRedis(db=2)
