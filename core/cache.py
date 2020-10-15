# coding: utf-8
from __future__ import unicode_literals
from core.utils import conf

import redis

client_redis_riddle = None

GLOBAL_CONF_KEY = 'riddle_global_conf'
WITHDRAW_CONF_KEY = 'riddle_global_conf'
VERIFY_CODE_KEY = '{0}_verify'
REWARD_KEY = 'reward_{0}'
EXPIRE_TIME = 300


def config_client_redis_zhz():
    global client_redis_riddle
    client_redis_riddle = redis.StrictRedis(db=int(conf.redis_db), host=conf.redis_host, port=int(conf.redis_port))


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