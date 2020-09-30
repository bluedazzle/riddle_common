# coding=utf-8
from __future__ import unicode_literals

import random

from django.core.management.base import BaseCommand

from account.models import User

class Command(BaseCommand):
    def invite_code_init(self, user_num):
        model = User
        for user_id in range(user_num):
            users = model.objects.filter(id=user_id).all()
            if not users.exists():
                continue
            user = users[0]
            if user.invite_code == '':
                user.invite_code = self.create_invite_code()
                user.save()


    def create_invite_code(self):
        invite_code = ''.join(
            random.sample('1234567890ZYXWVUTSRQPONMLKJIHGFEDCBAZYXWVUTSRQPONMLKJIHGFEDCBA', 8)).replace(" ", "")
        return invite_code


    def handle(self, *args, **options):
        self.invite_code_init(30000)