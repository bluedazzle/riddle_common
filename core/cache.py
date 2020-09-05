# coding: utf-8
from __future__ import unicode_literals
from core.utils import conf

import redis

client_redis_riddle = None

GLOBAL_CONF_KEY = 'riddle_global_conf'
VERIFY_CODE_KEY = '{0}_verify'
REWARD_KEY = 'reward_{0}'
EXPIRE_TIME = 300


def config_client_redis_zhz():
    global client_redis_riddle
    client_redis_riddle = redis.StrictRedis(db=2, host=conf.redis_host, port=int(conf.redis_port))


def get_global_config_from_cache():
    global client_redis_riddle
    client_redis_riddle.get(GLOBAL_CONF_KEY)


def set_global_config_to_cache(conf_data):
    global client_redis_riddle
    client_redis_riddle.set(GLOBAL_CONF_KEY, conf_data)


def set_verify_to_redis(code, phone, ttl=EXPIRE_TIME):
    global client_redis_riddle
    client_redis_riddle.set(VERIFY_CODE_KEY.format(phone), code, ttl)


def get_verify_from_redis(phone):
    global client_redis_riddle
    return client_redis_riddle.get(VERIFY_CODE_KEY.format(phone))
