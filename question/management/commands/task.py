# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
import pypinyin
import urllib2
import numpy as np
from operator import itemgetter

prefix = 'http://songs.guess-song.plutus-cat.com/'

def pingyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s


def song_init(execl, songs=0):
    df = pd.read_excel(execl, sheet_name=u'songs', encoding='utf-8')
    infos = df.ix[:, [u'歌手名', u'歌曲名']]
    if songs == 0:
        lines = len(infos[u'歌手名'])
    else:
        lines = songs
    for line in range(lines):
        url = prefix + pingyin(infos[u'歌手名'][line]) + '_' + pingyin(infos[u'歌曲名'][line]) + '.m4a'
        print url



def question_init(execl, questions=0):
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
        url = prefix + pingyin(infos[u'歌手名'][line]).replace('，', '') + '_' + pingyin(infos[u'歌曲名'][line]).replace('，', '') + '.m4a'
        try:
            resp = urllib2.urlopen(str(url))
        except:
            # print url
            continue
        if resp.getcode() != 200:
            continue
        questions1_list.append((int(infos[u'顺序id'][line]), int(infos[u'容易度'][line]), infos[u'歌曲名'][line], infos[u'错误歌曲名'][line], url))
    # sorted(questions1_list, key=itemgetter(0))
    questions1_list.sort(key=itemgetter(0))
    # print questions1_list
    for line in range(lines):
        if np.isnan(infos[u'顺序id'][line]):
            url = prefix + pingyin(infos[u'歌手名'][line]).replace('，', '') + '_' + pingyin(infos[u'歌曲名'][line]).replace('，', '') + '.m4a'
            try:
                resp = urllib2.urlopen(str(url))
            except:
                # print url
                continue
            if resp.getcode() != 200:
                continue
            questions2_list.append((infos[u'顺序id'][line], int(infos[u'容易度'][line]), infos[u'歌曲名'][line], infos[u'错误歌曲名'][line], url))
    # sorted(questions2_list, key=itemgetter(1))
    questions2_list.sort(key=itemgetter(1))
    # print questions2_list
    for item in questions2_list:
        questions1_list.append(item)
    # print questions1_list
    for num in range(len(questions1_list)):
        print num, questions1_list[num][1]




if __name__ == "__main__":
    question_init(u'songs.xlsx', 100)