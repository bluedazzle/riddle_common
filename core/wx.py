# coding: utf-8
from __future__ import unicode_literals

import json
import requests

# from django.core.cache import cache
# from django.utils import timezone
from core.pyutil.net.get_local_ip import get_local_ip

APP_KEY = 'wx0a70602b8b19b1e5'
APP_SECRET = '77b167cb1b9f4cc491010207d79b4f61'
WX_MCH_KEY = 'atpexFTVI97mPZfhwwlLdGdvuizulgyq'
WX_MCH_ID = '1602484372'


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
        raise ValueError(json_data.get('errmsg'))
    except Exception as e:
        raise e


def send_money_by_open_id(partner_trade_no, open_id, amount=30):
    from wx_pay import WxPay, WxPayError
    pay = WxPay(
        wx_app_id=APP_KEY,  # 微信平台appid
        wx_mch_id=WX_MCH_ID,  # 微信支付商户号
        wx_mch_key=WX_MCH_KEY,
        # wx_mch_key 微信支付重要密钥，请登录微信支付商户平台，在 账户中心-API安全-设置API密钥设置
        wx_notify_url='http://cc.rapo.cc:801/'
        # wx_notify_url 接受微信付款消息通知地址（通常比自己把支付成功信号写在js里要安全得多，推荐使用这个来接收微信支付成功通知）
        # wx_notify_url 开发详见https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_7
    )
    resp = pay.enterprise_payment(openid=open_id, check_name=False, amount=amount, desc='用户提现',
                                  partner_trade_no=partner_trade_no,
                                  spbill_create_ip=get_local_ip(),
                                  api_cert_path='/cert/apiclient_cert.pem',
                                  api_key_path='/cert/apiclient_key.pem')
    print resp


    # a = get_user_info('36_JfpsAim5IsbKJga0EIFmwPBilywps41UGGZeYpUnZsC8wSEy1RS92sxFm2oJP7a2uZcFJjIjjCxvBUwhoQiZa6T38FCGq9-CpzodaMlPFS8', 'oJhFr6Q66rQqXSE2nnBOBbNcchJ0')
    #
    # print a.get('province').encode('raw_unicode_escape')
