# coding=utf-8
import pandas as pd
import pypinyin

from question.models import Song
from question.models import Question

prefix = 'http://songs.guess-song.plutus-cat.com/'

def pingyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s

def song_init(execl, songs = 0):
    model = Song
    df = pd.read_excel(execl, sheet_name=u'曲库表')
    infos = df.ix[:, [u'歌手名', u'歌曲名']]
    if songs == 0:
        lines = len(infos[u'歌手名'])
    else:
        lines = songs
    for line in range(lines):
        url = prefix + pingyin(infos[u'歌手名'][line]) + '_' + pingyin(infos[u'歌曲名'][line]) + '.m4a'
        # print url
        objs = model.objects.filter(resource_url=url).all()
        if objs.exists():
            continue
        obj = model(singer=infos[u'歌手名'][line], name=infos[u'歌曲名'][line], resource_url=url)
        obj.save()

def question_init(execl, questions = 0):
    model = Question
    df = pd.read_excel(execl, sheet_name=u'曲库表')

if __name__ == "__main__":
    song_init('进度表及曲库.xlsx', 10)