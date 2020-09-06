# coding: utf-8
from __future__ import unicode_literals

import os
import json

os.environ['TRANSLATE_LAZY'] = '1'
from core.pyutil.conf2 import Conf

conf = Conf(os.getenv('RIDDLE_CONF_FILE') or os.path.join(os.path.dirname(os.path.dirname(__file__)), "conf/deploy.conf"))

is_debug = conf.debug == 'True'


def get_global_conf():
    from baseconf.models import GlobalConf
    from core.cache import get_global_config_from_cache, set_global_config_to_cache
    from core.dss.Serializer import serializer

    global_conf = get_global_config_from_cache()
    if not global_conf:
        obj = GlobalConf.objects.all()[0]
        global_conf = serializer(obj, output_type='json', exclude_attr=['create_time', 'modify_time'])
        set_global_config_to_cache(global_conf)
    return json.loads(global_conf)
