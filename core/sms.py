# coding: utf-8
# from __future__ import unicode_literals
import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

ACCESS_KEY = "LTAI4GBzg1ciDQJQDVWbkKWi"
ACCESS_SECRET = "BsTurISfu76CvFgNsVrPR8fmUpYFzP"


def send_sms_by_phone(phone, code):
    client = AcsClient(ACCESS_KEY, ACCESS_SECRET, 'cn-hangzhou')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', str(phone))
    request.add_query_param('SignName', "plutus喵")
    request.add_query_param('TemplateCode', "SMS_172886678")
    request.add_query_param('TemplateParam', {"code": str(code)})

    response = client.do_action_with_exception(request)
    json_data = json.loads(response)
    print(str(response))
    if json_data.get('Message', '') == 'OK':
        return True
    raise ValueError(json_data.get('Message', ''))


if __name__ == '__main__':
    pass
# print send_sms_by_phone(13000000000, 1234)
