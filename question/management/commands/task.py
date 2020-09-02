# coding=utf-8
from __future__ import unicode_literals

import pandas as pd

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def song_init(self, execl, songs=0):
        df = pd.read_excel(execl, sheet_name=u'曲库表')
        infos = df.ix[:, [u'歌手名', u'歌曲名']]

    def handle(self, *args, **options):
        # self.song_init(u'进度表及曲库.xlsx', 10)
        df = pd.read_excel(u'进度表及曲库.xlsx', sheet_name=u'曲库表')
        infos = df.ix[:, [u'歌手名', u'歌曲名']]