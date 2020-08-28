# coding=utf-8
import pandas as pd
import pypinyin

from question.models import Song

prefix = 'http://songs.guess-song.plutus-cat.com/'

def pingyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s

def song_init(execl):
    model = Song
    df = pd.read_excel(execl, sheet_name=u'曲库表')
    infos = df.ix[:, [u'歌手名', u'歌曲名']]
    lines = len(infos[u'歌手名'])
    for line in range(lines):
        url = prefix + pingyin(infos[u'歌手名'][line]) + '_' + pingyin(infos[u'歌曲名'][line]) + '.m4a'
        obj = model(singer=infos[u'歌手名'][line], name=infos[u'歌曲名'][line], resource_url=url)
        obj.save()


if __name__ == "__main__":
    song_init('进度表及曲库.xlsx')