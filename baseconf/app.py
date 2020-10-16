# coding: utf-8

from django.apps import AppConfig
from core.cache import update_ab_test_config_from_cache


class MyAppConfig(AppConfig):
    name = 'baseconf'

    def ready(self):
        update_ab_test_config_from_cache()
