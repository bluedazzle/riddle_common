# coding: utf-8
import logging

from django.utils.deprecation import MiddlewareMixin

from account.models import User
from core.cache import format_ab_test_config, is_ab_test_destroy_key_from_cache


class ABTestMiddleWare(MiddlewareMixin):
    @staticmethod
    def get_ab_test_id(user_id):
        try:
            ab_value = int(str(user_id)[-2:])
            config = format_ab_test_config()
            for k, v in config.items():
                if ab_value in v:
                    return k
        except Exception as e:
            logging.exception(e)
        return None

    def process_request(self, request):
        token = request.GET.get('token', None) or request.POST.get('token', None)
        user = None
        if not token:
            token = request.session.get('token', '')
        if token:
            user_list = User.objects.filter(token=token)
            if user_list.exists():
                user = user_list[0]
        setattr(request, 'account', user)
        if user:
            if not user.ab_test_id:
                ab_test_id = self.get_ab_test_id(user.id)
                if ab_test_id:
                    user.ab_test_id = ab_test_id
                    user.save()
            else:
                try:
                    slug, test_id = user.ab_test_id.split('&')
                    if is_ab_test_destroy_key_from_cache(slug):
                        ab_test_id = self.get_ab_test_id(user.id)
                        if ab_test_id:
                            user.ab_test_id = ab_test_id
                            user.save()
                except Exception as e:
                    logging.exception(e)
