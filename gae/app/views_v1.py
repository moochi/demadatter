#!/usr/bin/env python
# coding:utf-8


''' API エンドポイント
# エントリ投稿系
('/v2/api/post',  DemaAdd),
#('/v2/api/post/(.*)',  DemaAdd),
# エントリ情報取得 
('/v2/api/entry',  DemaGet),
# ランキング取得系
('/v2/api/ranking', DemaRanking),  
'''

import os, sys
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_dir, 'lib'))

import logging
import random, string
from flask import Module,  render_template
from flask import make_response, Response
from flask import request
from flask import json
from flask import redirect
import logging
import models
views_v1 = Module(__name__)

logging.getLogger().setLevel(logging.DEBUG)

@views_v1.route('/api/', methods=['GET', 'POST'])
def dema_ranking():
    return redirect('/v2/ranking')

@views_v1.route('/api/count', methods=['GET', 'POST'])
def dema_count():
    token = getToken(request.args.get('token'))
    tweetid = request.args.get('tweetid')
    result = ['token=%s' % token]
    tweet = get_twit(tweetid)
    if tweet:
        result.append('%s=%d' % (tweetid,tweet.dema_count))
    else:
        result.append('%s=0' % tweetid)
    result = '\n'.join(result)
    response = make_response(result)
    response.headers['Content-Type'] = "text/plain"
    response.headers['Content-Length'] = '%d' % len(result)
    return response

@views_v1.route('/add', methods=['GET', 'POST'])
def dema_add():
    token   = getToken(request.args.get('token'))
    result = ['token=%s' % token]

    tweetid = request.args.get('tweetid')
    # レポート追加
    # models.Report(token=token,tweetid=tweetid).put()
    # # ツイート更新
    # tweet = models.Tweet.all().filter('tweetid =', tweetid).get() or models.Tweet()
    # # ツイートID
    # tweet.tweetid = tweetid
    # # ツイート日時
    # tweet.createdat = datetime.fromtimestamp(float(request.args.get('created_at')))
    # # 本文
    # tweet.tweet = request.args.get('tweet')
    # # 発言者のスクリーンネーム
    # tweet.screen_name = request.args.get('screen_name')
    # # 発言者のユーザ名
    # tweet.user_name = request.args.get('user_name')
    # # レポート件数
    # tweet.count = models.Report.all().filter('tweetid =', tweetid).count()
    # # 保存
    # tweet.put()
    # result.append('%s=%d' % (tweetid, tweet.count))
    result.append('%s=%d' % (tweetid, 1))

    # 結果出力
    result = '\n'.join(result)
    response = make_response(result)
    response.headers['Content-Type'] = "text/plain"
    response.headers['Content-Length'] = '%d' % len(result)
    return response

def get_twit(tweet_id):
    #logging.debug('hoge %s' % (tweet_id))
    entity = models.Tweet.all().filter('tweet_id =',int(tweet_id)).get()
    return entity

def getToken(token):
    if not token:
        # 新しいトークンを発行
        token = ''.join(random.choice(string.ascii_letters) for i in range(20))
        models.User(token=token).put()
    return token

