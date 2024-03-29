# coding: utf-8
from __future__ import unicode_literals

from django.http import Http404
from django.http import HttpResponse


# Info Code

class ChoiceBase(object):
    '''
    __choices__每个元素的 key 和 value 都必须不同
    '''
    __choices__ = ()

    @classmethod
    def choices(cls):
        return cls.__choices__

    @classmethod
    def get_value(cls, key):
        _choices = dict(cls.__choices__)
        return _choices.get(key)

    @classmethod
    def get_key(cls, value):
        _value_to_key = {v: k for k, v in cls.__choices__}
        return _value_to_key.get(value)

    @classmethod
    def keys(cls):
        _dict = dict(cls.__choices__)
        return _dict.keys()

    @classmethod
    def values(cls):
        _dict = dict(cls.__choices__)
        return _dict.values()


class StatusCode(ChoiceBase):
    # 业务状态码

    INFO_SUCCESS = 0

    ERROR_UNKNOWN = 1000
    ERROR_DATA = 1001
    ERROR_TIMEOUT = 1002
    ERROR_FORM = 1003
    ERROR_PARAMETER = 1004
    ERROR_PAGE = 1005
    ERROR_VALIDATION = 1006

    ERROR_PERMISSION_DENIED = 2000
    ERROR_ACCOUNT_NO_EXIST = 2001
    ERROR_PASSWORD = 2002
    ERROR_NO_VERIFY = 2003
    ERROR_VERIFY = 2004
    ERROR_PHONE_EXIST = 2005
    ERROR_PHONE_BIND = 2006
    ERROR_INVITE_CODE = 2007
    ERROR_INVITE_BONUS = 2008
    ERROR_BONUS_OVER = 2009
    ERROR_BONUS_LESS = 2010
    ERROR_INVITE_EXIST = 2011
    ERROR_INVITER_CODE = 2012

    ERROR_QUESTION_ORDER = 3001
    ERROR_STIMULATE_TAG = 3002
    ERROR_QUESTION_NONE = 3003

    ERROR_NOT_ALLOW_CASH = 4000
    ERROR_REPEAT_NEW_PACKET = 4001
    ERROR_REWARD_DENIED = 4002

    ERROR_TASK_FINISHED = 5001
    ERROR_TASK_NOT_EXIST = 5002

    __choices__ = (
        (INFO_SUCCESS, u'成功'),
        (ERROR_UNKNOWN, u'未知错误'),
        (ERROR_TIMEOUT, u'超时'),
        (ERROR_FORM, u'表单错误'),
        (ERROR_DATA, u'数据错误'),
        (ERROR_PARAMETER, u'参数错误'),
        (ERROR_PAGE, u'分页错误'),
        (ERROR_VALIDATION, u'校验错误'),
        (ERROR_PERMISSION_DENIED, u'权限不足'),
        (ERROR_ACCOUNT_NO_EXIST, u'账号不存在'),
        (ERROR_PASSWORD, u'密码错误'),
        (ERROR_NO_VERIFY, u'验证码缺失'),
        (ERROR_VERIFY, u'验证码错误/过期'),
        (ERROR_QUESTION_ORDER, u'答题顺序不正确'),
        (ERROR_STIMULATE_TAG, u'激励验证错误'),
        (ERROR_QUESTION_NONE, u'答题序号不存在'),
        (ERROR_PHONE_EXIST, u'手机号已存在'),
        (ERROR_NOT_ALLOW_CASH, u'未到提现门槛'),
        (ERROR_PHONE_BIND, u'账号已绑定手机'),
        (ERROR_REPEAT_NEW_PACKET, u'新人红包不可重复领取'),
        (ERROR_REWARD_DENIED, u'无抽奖权限'),
        (ERROR_INVITE_CODE, u'邀请码不存在'),
        (ERROR_INVITE_BONUS, u'领取奖励参数错误'),
        (ERROR_BONUS_OVER, u'奖励已领取'),
        (ERROR_BONUS_LESS, u'尚未达到领取资格'),
        (ERROR_INVITE_EXIST, u'邀请人已存在'),
        (ERROR_INVITER_CODE, u'您的注册时间早于邀请人，无法被邀请'),
        (ERROR_TASK_FINISHED, u'任务已完成'),
        (ERROR_TASK_NOT_EXIST, u'任务不存在'),
    )


class StatusWrapMixin(object):
    status_code = StatusCode.INFO_SUCCESS
    message = StatusCode.get_value(StatusCode.INFO_SUCCESS)

    def update_status(self, key):
        self.status_code = key
        self.message = StatusCode.get_value(key)

    def render_to_response(self, context={}, extra={}, **response_kwargs):
        context_dict = self.context_serialize(context)
        json_context = self.json_serializer(self.wrapper(context_dict, extra))
        return HttpResponse(json_context, content_type='application/json', **response_kwargs)

    def wrapper(self, context, extra):
        return_data = dict()
        return_data['data'] = context
        return_data['extra'] = extra
        return_data['code'] = self.status_code
        return_data['msg'] = self.message
        if self.status_code != StatusCode.INFO_SUCCESS:
            return_data['data'] = {}
        return return_data

        # todo

        # def dispatch(self, request, *args, **kwargs):
        #     try:
        #         return super(StatusWrapMixin, self).dispatch(self, request, *args, **kwargs)
        #     except Http404 as e:
        #         self.status_code = INFO_NO_EXIST
        #         self.message = '不存在'
        #         return self.render_to_response()


class AdminStatusWrapMixin(StatusWrapMixin):
    def wrapper(self, context):
        data = super(AdminStatusWrapMixin, self).wrapper(context)
        if isinstance(self.message, unicode):
            data['msg'] = {'message': self.message}
            return data
        error_data = {}
        if isinstance(self.message, list):
            for itm in self.message:
                error_data[itm[0]] = itm[1]
        if isinstance(self.message, dict):
            for k, v in self.message.iteritems():
                error_data[k] = v[0].get('message', '')
        data['msg'] = error_data
        return data
