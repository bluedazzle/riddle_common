# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
import pypinyin
import requests
import random
import string
import numpy as np
from operator import itemgetter

from django.core.management.base import BaseCommand

from question.models import Song
from question.models import Question

prefix = 'http://songs.guess-song.plutus-cat.com/'


class Command(BaseCommand):
    def pingyin(self, word):
        s = ''
        for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
            s += ''.join(i)
        return s

    def song_init(self, execl, songs=0):
        model = Song
        df = pd.read_excel(execl, sheet_name=u'songs', encoding='utf-8')
        infos = df.ix[:, [u'歌手名', u'正确歌曲名']]
        if songs == 0:
            lines = len(infos[u'歌手名'])
        else:
            lines = songs
        for line in range(lines):
            url = prefix + self.pingyin(infos[u'歌手名'][line]) + '_' + self.pingyin(infos[u'正确歌曲名'][line]) + '.m4a'
            print(url)
            objs = model.objects.filter(resource_url=url).all()
            if objs.exists():
                continue
            obj = model(singer=infos[u'歌手名'][line], name=infos[u'正确歌曲名'][line], resource_url=url)
            obj.save()

    def question_init(self, execl, questions=0):
        model_question = Question
        model_song = Song
        df = pd.read_excel(execl, sheet_name=u'songs', encoding='utf-8')
        infos = df.ix[:, [u'是否完成', u'歌手名', u'正确歌曲名', u'容易度', u'新的顺序id', u'错误歌手名', u'错误歌曲名']]
        questions_list = []
        questions_singer_list = []
        model_question.objects.all().delete()
        model_song.objects.all().delete()
        questions_song = 0

        if questions == 0:
            lines = len(infos[u'歌手名'])
        else:
            lines = questions
        for line in range(lines):
            if pd.isna(infos[u'是否完成'][line]) or pd.isna(infos[u'歌手名'][line]) or pd.isna(infos[u'正确歌曲名'][line]) \
                    or pd.isna(infos[u'容易度'][line]) or pd.isna(infos[u'错误歌曲名'][line]):
                continue
            url = prefix + self.pingyin(infos[u'歌手名'][line]).replace('，', '') + '_' + self.pingyin(
                infos[u'正确歌曲名'][line]).replace('，', '') + '.m4a'
            try:
                resp = requests.get(str(url), timeout=4)
            except:
                continue
            if resp.status_code != 200:
                continue
            tag = ''.join(
                random.sample(
                    'ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                    32)).replace(" ", "")
            questions_list.append((int(infos[u'容易度'][line]), infos[u'歌手名'][line],
                                   infos[u'正确歌曲名'][line], infos[u'错误歌曲名'][line], url, infos[u'新的顺序id'][line], tag))
        questions_list.sort(key=lambda x: (x[0], x[5], x[6]))

        for num in range(len(questions_list)):
            questions_song += 1
            obj_question = model_question(title=u'猜猜这首歌叫什么', order_id=num + 1, question_type=1,
                                          difficult=questions_list[num][0],
                                          right_answer_id=1, right_answer=questions_list[num][2],
                                          wrong_answer_id=2, wrong_answer=questions_list[num][3],
                                          resource_url=questions_list[num][4])
            obj_question.save()
            obj_song = model_song(singer=questions_list[num][1], name=questions_list[num][2],
                                  resource_url=questions_list[num][4])
            obj_song.save()

            # init the singer questions
        for line in range(lines):
            if pd.isna(infos[u'是否完成'][line]) or pd.isna(infos[u'歌手名'][line]) or pd.isna(infos[u'正确歌曲名'][line]) \
                    or pd.isna(infos[u'容易度'][line]) or pd.isna(infos[u'错误歌手名'][line]):
                continue
            url = prefix + self.pingyin(infos[u'歌手名'][line]).replace('，', '') + '_' + self.pingyin(
                infos[u'正确歌曲名'][line]).replace('，', '') + '.m4a'
            try:
                resp = requests.get(str(url), timeout=4)
            except:
                continue
            if resp.status_code != 200:
                continue
            tag = ''.join(
                        random.sample(
                            'ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                            32)).replace(" ", "")
            questions_singer_list.append((int(infos[u'容易度'][line]), infos[u'歌手名'][line],
                                    infos[u'正确歌曲名'][line], infos[u'错误歌手名'][line], url, infos[u'新的顺序id'][line], tag))
        questions_singer_list.sort(key=lambda x: (x[0], x[5], x[6]))

        for num in range(len(questions_singer_list)):
            obj_question = model_question(title=u'猜猜歌手叫什么', order_id=num+questions_song+1, question_type=2, difficult=questions_singer_list[num][0],
                        right_answer_id=1, right_answer=questions_singer_list[num][1],
                        wrong_answer_id=2, wrong_answer=questions_singer_list[num][3], resource_url=questions_singer_list[num][4])
            obj_question.save()

    def handle(self, *args, **options):
        # self.song_init(u'question/management/commands/songs.xlsx', 100)
        self.question_init(u'question/management/commands/songs.xlsx', 908)
