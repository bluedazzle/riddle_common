# coding=utf-8
from __future__ import unicode_literals

import pandas as pd
from urllib import parse
import pypinyin
import requests

prefix = 'http://cai-ta.ecdn.plutus-cat.com/assets/'

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
        print(url)



def question_init(execl, questions=0):
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
            pic = infos[u'正确答案'][line] + '/' + infos[u'正确答案'][line] + '-' + str(name_dic[infos[u'正确答案'][line]]) + '.jpg'
            encode_pic = parse.quote(pic)
            url = prefix + encode_pic
            try:
                resp = requests.get(str(url), timeout=4)
            except :
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
        questions_list.append((infos[u'id'][line], infos[u'题目顺序'][line], infos[u'题目类型'][line],
                               infos[u'正确答案'][line], infos[u'错误答案'][line], pics_list))

    questions_list.sort(key=lambda x: (x[1]))
    print("total: " + str(len(questions_list)))
    print(questions_list)





if __name__ == "__main__":
    question_init(u'questions.xlsx', 100)

    # pic = '刘亦菲/刘亦菲－1' + '.jpg'
    # encode_pic = parse.quote(pic)
    # url = prefix + encode_pic
    #
    # print(url)
    # resp = requests.get(url, timeout=4)
    # if resp.status_code != 200:
    #     print("success!")