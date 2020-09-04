# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
import pypinyin
import urllib2
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

    # def song_init(self, execl, songs=0):
    #     model = Song
    #     df = pd.read_excel(execl, sheet_name=u'songs', encoding='utf-8')
    #     infos = df.ix[:, [u'歌手名', u'歌曲名']]
    #     if songs == 0:
    #         lines = len(infos[u'歌手名'])
    #     else:
    #         lines = songs
    #     for line in range(lines):
    #         url = prefix + self.pingyin(infos[u'歌手名'][line]) + '_' + self.pingyin(infos[u'歌曲名'][line]) + '.m4a'
    #         print url
    #         objs = model.objects.filter(resource_url=url).all()
    #         if objs.exists():
    #             continue
    #         obj = model(singer=infos[u'歌手名'][line], name=infos[u'歌曲名'][line], resource_url=url)
    #         obj.save()

    def question_init(self, execl, questions=0):
        model_question = Question
        model_song = Song
        df = pd.read_excel(execl, sheet_name=u'songs', encoding='utf-8')
        infos = df.ix[:, [u'歌手名', u'歌曲名', u'容易度', u'错误歌曲名', u'顺序id']]
        questions1_list = []
        questions2_list = []
        if questions == 0:
            lines = len(infos[u'歌手名'])
        else:
            lines = questions
        for line in range(lines):
            if np.isnan(infos[u'顺序id'][line]):
                continue
            url = prefix + self.pingyin(infos[u'歌手名'][line]) + '_' + self.pingyin(infos[u'歌曲名'][line]) + '.m4a'
            objs = model_question.objects.filter(resource_url=url).all()
            if objs.exists():
                continue
            try:
                resp = urllib2.urlopen(str(url))
            except:
                continue
            if resp.getcode() != 200:
                continue
            questions1_list.append((int(infos[u'顺序id'][line]), int(infos[u'容易度'][line]),
                                    infos[u'歌手名'][line], infos[u'歌曲名'][line], infos[u'错误歌曲名'][line], url))
            questions1_list.sort(key=itemgetter(0))
        for line in range(lines):
            if np.isnan(infos[u'顺序id'][line]):
                url = prefix + self.pingyin(infos[u'歌手名'][line]).replace('，', '') + '_' + self.pingyin(
                    infos[u'歌曲名'][line]).replace('，', '') + '.m4a'
                try:
                    resp = urllib2.urlopen(str(url))
                except:
                    continue
                if resp.getcode() != 200:
                    continue
                questions2_list.append((infos[u'顺序id'][line], int(infos[u'容易度'][line]),
                                        infos[u'歌手名'][line], infos[u'歌曲名'][line], infos[u'错误歌曲名'][line], url))
        questions2_list.sort(key=itemgetter(1))
        for item in questions2_list:
            questions1_list.append(item)

        for num in range(len(questions1_list)):
            obj_question = model_question(title=u'猜猜这首歌叫什么', order_id=num+1, question_type=1, difficult=questions1_list[num][1],
                        right_answer_id=1, right_answer=questions1_list[num][3],
                        wrong_answer_id=2, wrong_answer=questions1_list[num][4], resource_url=questions1_list[num][5])
            obj_question.save()
            obj_song = model_song(singer=questions1_list[num][2], name=questions1_list[num][3], resource_url=questions1_list[num][5])
            obj_song.save()

    def handle(self, *args, **options):
        # self.song_init(u'question/management/commands/songs.xlsx', 100)
        self.question_init(u'question/management/commands/songs.xlsx', 100)
