# coding: utf-8
from __future__ import unicode_literals

import os

os.environ['TRANSLATE_LAZY'] = '1'
from core.pyutil.conf2 import Conf

conf = Conf(os.path.join(os.path.dirname(os.path.dirname(__file__)), "conf/deploy.conf"))

is_debug = conf.debug == 'True'
