# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
import pypinyin

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
        df = pd.read_excel(execl, sheet_name=u'曲库表', encoding='utf-8')
        infos = df.ix[:, [u'歌手名', u'歌曲名']]
        if songs == 0:
            lines = len(infos[u'歌手名'])
        else:
            lines = songs
        for line in range(lines):
            url = prefix + self.pingyin(infos[u'歌手名'][line]) + '_' + self.pingyin(infos[u'歌曲名'][line]) + '.m4a'
            print url
            objs = model.objects.filter(resource_url=url).all()
            if objs.exists():
                continue
            obj = model(singer=infos[u'歌手名'][line], name=infos[u'歌曲名'][line], resource_url=url)
            obj.save()

    def question_init(self, execl, questions=0):
        model = Question
        df = pd.read_excel(execl, sheet_name=u'曲库表', encoding='utf-8')
        infos = df.ix[:, [u'歌手名', u'歌曲名', u'容易度', u'错误歌曲名']]
        if questions == 0:
            lines = len(infos[u'歌手名'])
        else:
            lines = questions
        for line in range(lines):
            url = prefix + self.pingyin(infos[u'歌手名'][line]) + '_' + self.pingyin(infos[u'歌曲名'][line]) + '.m4a'
            objs = model.objects.filter(resource_url=url).all()
            if objs.exists():
                continue
            obj = model(title=u'猜猜这首歌叫什么', order_id=line+1, question_type=1, difficult=infos[u'容易度'][line],
                        right_answer_id=1, right_answer=infos[u'歌曲名'][line],
                        wrong_answer_id=2, wrong_answer=infos[u'错误歌曲名'][line], resource_url=url)
            obj.save()

    def handle(self, *args, **options):
        self.song_init(u'question/management/commands/进度表及曲库.xlsx', 100)
        self.question_init(u'question/management/commands/进度表及曲库.xlsx', 100)
