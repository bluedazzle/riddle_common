# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
import pypinyin
import urllib2
import numpy as np

prefix = 'http://songs.guess-song.plutus-cat.com/'
cycle = 0
index = 0

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
    questions_list = []
    if questions == 0:
        lines = len(infos[u'歌手名'])
    else:
        lines = questions
    for line in range(lines):
        if np.isnan(infos[u'顺序id'][line]):
            continue
        url = prefix + pingyin(infos[u'歌手名'][line]) + '_' + pingyin(infos[u'歌曲名'][line]) + '.m4a'
        try:
            resp = urllib2.urlopen(str(url))
        except:
            continue
        if resp.getcode() != 200:
            continue
        questions_list.append((int(infos[u'顺序id'][line]), infos[u'容易度'][line], infos[u'歌曲名'][line], infos[u'错误歌曲名'][line], url))
    print sorted(questions_list)




if __name__ == "__main__":
    question_init(u'songs.xlsx', 100)