# coding: utf-8
from __future__ import unicode_literals

import json

import logging

from core.consts import STATUS_DESTROY, STATUS_ENABLE
from core.utils import conf

import redis

client_redis_riddle = None
client_redis_ab_test = None

GLOBAL_CONF_KEY = 'riddle_global_conf'
WITHDRAW_CONF_KEY = 'riddle_global_conf'
VERIFY_CODE_KEY = '{0}_verify'
REWARD_KEY = 'reward_{0}'
EXPIRE_TIME = 300
RD_AB_TEST_KEY = 'ab_test_config'
RD_AB_DEST_KEY = 'ab_test_destroy'
RD_DAILY_TASK_CONF_KEY = 'daily_task_config'
RD_COMMON_TASK_CONF_KEY = 'common_task_config'
RD_TASK_ID_PREFIX = 'task_id_{0}'


def config_client_redis_zhz():
    global client_redis_riddle
    client_redis_riddle = redis.StrictRedis(db=int(conf.redis_db), host=conf.redis_host, port=int(conf.redis_port))


def config_redis_ab_test():
    global client_redis_ab_test
    client_redis_ab_test = redis.StrictRedis(db=int(3), host=conf.redis_host,
                                             port=int(conf.redis_port))


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


class RedisProxy(object):
    def __init__(self, redis, base_key, pk=None, props=[]):
        self.redis = redis
        self.base_key = base_key
        self.props = props
        self.pk = pk

    def encode_value(self, *args):
        value = args[0]
        for arg in args[1:]:
            value = '{0}|$|{1}'.format(value, arg)
        return value

    def decode_value(self, itm):
        if not itm:
            return {}
        value_list = itm.decode('utf-8').split('|$|')
        value_dict = {}
        for index, value in enumerate(value_list):
            value_dict[self.props[index]] = value
        return value_dict

    def remove_member_from_set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        return self.redis.srem(key, value)

    def get_set_count(self, key):
        key = self.base_key.format(key)
        count = self.redis.scard(key)
        return count

    def get_set_members(self, key):
        key = self.base_key.format(key)
        result = self.redis.smembers(key)
        member_list = []
        for itm in result:
            member_list.append(self.decode_value(itm))
        return member_list

    def exist(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        res = self.redis.sismember(key, value)
        return res

    def search(self, key, pk):
        if not self.pk:
            return False, None
        mem_list = self.get_set_members(key)
        for itm in mem_list:
            itm = self.decode_value(itm)
            if itm.get(self.pk) == pk:
                return True, itm
        return False, None

    def create_update_set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.sadd(key, value)


class KVRedisProxy(RedisProxy):
    def set(self, key, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.set(key, value)

    def setex(self, key, t, *args):
        key = self.base_key.format(key)
        value = self.encode_value(*args)
        self.redis.setex(key, t, value)

    def get(self, key):
        key = self.base_key.format(key)
        result = self.redis.get(key)
        return self.decode_value(result)

    def mget(self, keys):
        base_keys = [self.base_key.format(itm) for itm in keys]
        result = self.redis.mget(base_keys)
        return [self.decode_value(itm) for itm in result]


def update_ab_test_config_from_cache():
    global client_redis_ab_test
    from baseconf.models import ABTest
    objs = ABTest.objects.filter(status=STATUS_ENABLE).order_by('-create_time').all()
    config = []
    for obj in objs:
        cf = {}
        cf['aid'] = obj.id
        cf['slug'] = obj.slug
        cf['astart'] = obj.test_a_start_value
        cf['aend'] = obj.test_a_end_value
        cf['bstart'] = obj.test_b_start_value
        cf['bend'] = obj.test_b_end_value
        config.append(cf)
    client_redis_ab_test.set(RD_AB_TEST_KEY, json.dumps(config))
    objs = ABTest.objects.filter(status=STATUS_DESTROY).order_by('-create_time').all()
    client_redis_ab_test.delete(RD_AB_DEST_KEY)
    for obj in objs:
        client_redis_ab_test.sadd(RD_AB_DEST_KEY, obj.slug)


def get_ab_test_config_from_cache():
    global client_redis_ab_test
    res = client_redis_ab_test.get(RD_AB_TEST_KEY)
    if not res:
        return []
    config = json.loads(res)
    return config


def get_daily_task_config_from_cache():
    global client_redis_riddle
    res = client_redis_riddle.get(RD_DAILY_TASK_CONF_KEY)
    if not res:
        return []
    config = json.loads(res)
    return config


def set_daily_task_config_to_cache(config):
    global client_redis_riddle
    res = client_redis_riddle.set(RD_DAILY_TASK_CONF_KEY, config)
    return res


def get_common_task_config_from_cache():
    global client_redis_riddle
    res = client_redis_riddle.get(RD_COMMON_TASK_CONF_KEY)
    if not res:
        return []
    config = json.loads(res)
    return config


def set_common_task_config_to_cache(config):
    global client_redis_riddle
    res = client_redis_riddle.set(RD_COMMON_TASK_CONF_KEY, config)
    return res


def search_task_id_by_cache(task_id):
    global client_redis_riddle
    res = client_redis_riddle.get(RD_TASK_ID_PREFIX.format(task_id))
    if not res:
        return False
    return True


def set_task_id_to_cache(task_id, ttl=None):
    global client_redis_riddle
    if ttl:
        res = client_redis_riddle.setex(RD_TASK_ID_PREFIX.format(task_id), ttl, 1)
    else:
        res = client_redis_riddle.set(RD_TASK_ID_PREFIX.format(task_id), 1)
    if not res:
        return False
    return True


def format_ab_test_config():
    config = get_ab_test_config_from_cache()
    config_dict = {}
    for itm in config:
        ab_test_id = '{0}&1'.format(itm['slug'])
        id_range = set(range(itm['astart'], itm['aend'] + 1))
        config_dict[ab_test_id] = id_range
        ab_test_id = '{0}&2'.format(itm['slug'])
        id_range = set(range(itm['bstart'], itm['bend'] + 1))
        config_dict[ab_test_id] = id_range
    return config_dict


def is_ab_test_destroy_key_from_cache(key):
    global client_redis_ab_test
    if not client_redis_ab_test.exists(RD_AB_DEST_KEY):
        return False
    res = client_redis_ab_test.sismember(RD_AB_DEST_KEY, key)
    return True if res else False
