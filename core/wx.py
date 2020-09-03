# coding: utf-8
from __future__ import unicode_literals

import json
import requests

from django.core.cache import cache
from django.utils import timezone

APP_KEY = 'wx0a70602b8b19b1e5'
APP_SECRET = '77b167cb1b9f4cc491010207d79b4f61'


def get_access_token(source='riddle'):
    access_token = cache.get('{0}_access_token'.format(source))
    app_key, app_secret = APP_KEY, APP_SECRET
    if access_token:
        return access_token
    res = requests.get(
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(app_key,
                                                                                                           app_secret))
    json_data = json.loads(res.content)
    access_token = json_data.get('access_token', None)
    if access_token:
        cache.set('{0}_access_token'.format(source), access_token, 60 * 60 * 2)
        return access_token
    return None


def send_template_message(feedback):
    access_token = get_access_token()
    url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={0}'.format(access_token)
    time = feedback.create_time
    time = time.astimezone(timezone.get_current_timezone())
    data = {'touser': feedback.author.openid,
            'template_id': 'WcNGPs2DNoa6-hi3WrpxGT4x8CSFx2UFT8pnXlah15c',
            'form_id': feedback.form_id,
            'data': {
                "keyword1": {"value": time.strftime("%Y-%m-%d %H:%M:%S")},
                "keyword2": {"value": feedback.content},
                "keyword3": {"value": feedback.reply}
            }}
    res = requests.post(url, data=json.dumps(data)).content
    json_data = json.loads(res)
    status = json_data.get('errcode')
    if status == 0:
        return True
    return False


def get_session_key(code, source='old'):
    APP_KEY, APP_SECRET = get_key(source)
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
        APP_KEY, APP_SECRET, code)
    res = requests.get(url).content
    json_data = json.loads(res)
    openid = json_data.get('unionid', None) or json_data.get('openid', None)
    session = json_data.get('session_key', None)
    if openid and session:
        return True, openid, session
    return False, None, None


def get_access_token_by_code(code):
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code'.format(
        APP_KEY, APP_SECRET, code)
    try:
        resp = requests.get(url, timeout=3)
        json_data = resp.json()
        print json_data
        if not json_data.get('errcode'):
            return json_data
        raise ValueError(json_data.get('errmsg'))
    except Exception as e:
        raise e


def get_user_info(access_token, open_id):
    url = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'.format(access_token, open_id)
    try:
        resp = requests.get(url, timeout=3)
        json_data = resp.json()
        print json_data
        if not json_data.get('errcode'):
            return json_data
    except Exception as e:
        raise e
