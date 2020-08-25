# coding: utf-8

from __future__ import unicode_literals

import hashlib

import datetime
import json
import time

from django.utils.http import cookie_date
from django.utils.timezone import get_current_timezone
from django.http import HttpResponseRedirect

from smart_admin.models import Account
from api.models import Site
from core.Mixin.StatusWrapMixin import ERROR_PERMISSION_DENIED, ERROR_TOKEN, INFO_EXPIRE


# class CheckSecurityMixin(object):
#     secret = None
#     expire = datetime.timedelta(seconds=30)
#
#     def get_current_secret(self):
#         self.secret = Secret.objects.all()[0].secret
#         return self.secret
#
#     def check_expire(self):
#         timestamp = int(self.request.GET.get('timestamp', 0))
#         request_time = datetime.datetime.fromtimestamp(timestamp, tz=get_current_timezone())
#         now_time = datetime.datetime.now(tz=get_current_timezone())
#         if now_time - request_time > self.expire:
#             self.message = '请求超时,请重新验证'
#             self.status_code = INFO_EXPIRE
#             return False
#         else:
#             return True
#
#     def check_sign(self):
#         # timestamp = self.request.GET.get('timestamp', '')
#         # sign = unicode(self.request.GET.get('sign', '')).upper()
#         # check = unicode(hashlib.md5('{0}{1}'.format(timestamp, self.secret)).hexdigest()).upper()
#         # if check == sign:
#         #     return True
#         return True
#
#     def wrap_check_sign_result(self):
#         # if not self.check_expire():
#         #     self.message = 'sign 已过期'
#         #     self.status_code = ERROR_PERMISSION_DENIED
#         #     return False
#         self.get_current_secret()
#         result = self.check_sign()
#         if not result:
#             self.message = 'sign 验证失败'
#             self.status_code = ERROR_PERMISSION_DENIED
#             return False
#         return True
#
#     def get(self, request, *args, **kwargs):
#         if not self.wrap_check_sign_result():
#             return self.render_to_response(dict())
#         return super(CheckSecurityMixin, self).get(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         if not self.wrap_check_sign_result():
#             return self.render_to_response(dict())
#         return super(CheckSecurityMixin, self).post(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         if not self.wrap_check_sign_result():
#             return self.render_to_response(dict())
#         return super(CheckSecurityMixin, self).put(request, *args, **kwargs)
#
#     def patch(self, request, *args, **kwargs):
#         if not self.wrap_check_sign_result():
#             return self.render_to_response(dict())
#         return super(CheckSecurityMixin, self).patch(request, *args, **kwargs)
#
#
# class CheckTokenMixin(object):
#     token = None
#     user = None
#
#     def get_current_token(self):
#         self.token = self.request.GET.get('token', None) or self.request.POST.get('token', None)
#         if not self.token:
#             self.token = self.request.session.get(
#                 'token', '')
#         return self.token
#
#     def check_token(self):
#         self.get_current_token()
#         user_list = PartyUser.objects.filter(token=self.token)
#         if user_list.exists():
#             self.user = user_list[0]
#             return True
#         return False
#
#     def wrap_check_token_result(self):
#         result = self.check_token()
#         if not result:
#             self.message = 'token 错误, 请重新登陆'
#             self.status_code = ERROR_TOKEN
#             return False
#         return True
#
#
class CheckAdminPermissionMixin(object):
    token = None
    admin = None
    site = None

    def get_current_token(self):
        self.token = self.request.GET.get('token') or self.request.POST.get('token', '')
        return self.token

    def check_token(self):
        self.get_current_token()
        admin_list = Account.objects.filter(token=self.token)
        if admin_list.exists():
            self.admin = admin_list[0]
            self.site = admin_list[0].belong
            return True
        return False

    def wrap_check_token_result(self):
        result = self.check_token()
        if not result:
            self.message = 'token已过期, 请重新登陆'
            self.status_code = ERROR_TOKEN
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response()
        return super(CheckAdminPermissionMixin, self).dispatch(request, *args, **kwargs)


#
# class CheckAdminPagePermissionMixin(object):
#     def dispatch(self, request, *args, **kwargs):
#         token = request.session.get('token')
#         if token:
#             if HAdmin.objects.filter(token=token).exists():
#                 return super(CheckAdminPagePermissionMixin, self).dispatch(request, *args, **kwargs)
#         return HttpResponseRedirect('/admin/login')


class CheckSiteMixin(object):
    site = None
    site_slug = None

    def dispatch(self, request, *args, **kwargs):
        token = request.COOKIES.get('token', None) or request.GET.get('token', None) or request.POST.get('token', None)
        queryset = Site.objects.filter(slug=token)
        if queryset.exists():
            self.site = queryset[0]
            self.site_slug = token
            return super(CheckSiteMixin, self).dispatch(request, *args, **kwargs)
        self.message = '缺失站点信息'
        self.status_code = ERROR_PERMISSION_DENIED
        return self.render_to_response()

    def get_queryset(self):
        queryset = super(CheckSiteMixin, self).get_queryset()
        queryset = queryset.filter(belong=self.site)
        return queryset

    def render_to_response(self, context={}, **response_kwargs):
        resp = super(CheckSiteMixin, self).render_to_response(context, **response_kwargs)
        # expire = cookie_date(time.time() + 86400)
        # resp.set_cookie(key='token', value=self.site_slug, expires=expire)
        return resp
