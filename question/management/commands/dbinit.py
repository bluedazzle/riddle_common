# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
from urllib import parse
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
        df = pd.read_excel(execl, sheet_name=u'questions', encoding='utf-8')
        infos = df.ix[:, [u'id', u'题目顺序', u'题目类型', u'正确答案', u'错误答案']]
        questions_list = []
        name_dic = {}
        if questions == 0:
            lines = len(infos[u'id'])
        else:
            lines = questions
        for line in range(lines):
            pics_list = []
            pics_num = 0
            try_num = 0
            try_total = 0
            if pd.isna(infos[u'id'][line]) or pd.isna(infos[u'题目顺序'][line]) or pd.isna(infos[u'题目类型'][line]) \
                    or pd.isna(infos[u'正确答案'][line]) or pd.isna(infos[u'错误答案'][line]):
                continue
            if not name_dic.get(infos[u'正确答案'][line]):
                name_dic[infos[u'正确答案'][line]] = 1

            while pics_num < 3:
                pic = infos[u'正确答案'][line] + '/' + infos[u'正确答案'][line] + '-' + str(
                    name_dic[infos[u'正确答案'][line]]) + '.jpg'
                encode_pic = parse.quote(pic)
                url = prefix + encode_pic
                try:
                    resp = requests.get(str(url), timeout=4)
                except:
                    try_num = try_num + 1
                    name_dic[infos[u'正确答案'][line]] = name_dic[infos[u'正确答案'][line]] + 1
                    if try_num >= 3:
                        try_num = 0
                        name_dic[infos[u'正确答案'][line]] = 0
                    continue
                if resp.status_code != 200:
                    try_num = try_num + 1
                    name_dic[infos[u'正确答案'][line]] = name_dic[infos[u'正确答案'][line]] + 1
                    if try_num >= 3:
                        try_num = 0
                        name_dic[infos[u'正确答案'][line]] = 0
                    continue
                try_num = 0
                try_total = try_total + 1
                if try_total == 12:
                    break
                name_dic[infos[u'正确答案'][line]] = name_dic[infos[u'正确答案'][line]] + 1
                pics_num = pics_num + 1
                pics_list.append(url)
            if pics_num < 3:
                continue
            print(pics_list)
            questions_list.append((int(infos[u'id'][line]), int(infos[u'题目顺序'][line]), int(infos[u'题目类型'][line]),
                                   infos[u'正确答案'][line], infos[u'错误答案'][line], pics_list))

        questions_list.sort(key=lambda x: (x[1]))

        for num in range(len(questions_list)):
            obj_question = model_question(title=u'猜猜这是谁？', order_id=questions_list[num][0], question_type=1,
                                          difficult=1,
                                          right_answer_id=1, right_answer=questions_list[num][3],
                                          wrong_answer_id=2, wrong_answer=questions_list[num][4],
                                          resource_type=questions_list[num][2], resources=questions_list[num][4])
            obj_question.save()


    def handle(self, *args, **options):
        # self.song_init(u'question/management/commands/songs.xlsx', 100)
        self.question_init(u'question/management/commands/songs.xlsx', 908)
