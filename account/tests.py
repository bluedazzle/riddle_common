import json
from importlib import import_module

from django.conf import settings
from django.test import TestCase


# Create your tests here.


class TestUserInfo(TestCase):
    def setUp(self):
        self.token = ''
        resp = self.client.post('/api/v1/user/register/')
        self.assertEqual(resp.status_code, 200)
        user = resp.json().get('data').get('user')
        self.assertIsNotNone(user)
        self.token = user.get('token')

    def test_user_info(self):
        resp = self.client.get('/api/v1/user/info/?token={0}'.format(self.token))
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)
        print(json_data)
        self.assertIsNotNone(json_data.get('data').get('user'))
