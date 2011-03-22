# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import models

__all__ = ('DemaAdd', 'DemaCount')


class DemaAdd(webapp.RequestHandler):
    """デマレポート処理"""
    def post(self):
        # ユーザ認証
        token = getToken(self.request.get('token'))
        result = ['token=%s' % token]

        tweetid = self.request.get('tweetid')

        # レポート追加
        models.Report(token=token, tweetid=tweetid).put()

        # ツイート更新
        tweet = models.Tweet.all().filter('tweetid =', tweetid).get() or models.Tweet()
        # ツイートID
        tweet.tweetid = tweetid
        # ツイート日時
        tweet.createdat = datetime.fromtimestamp(float(self.request.get('created_at')))
        # 本文
        tweet.tweet = self.request.get('tweet')
        # 発言者のスクリーンネーム
        tweet.screen_name = self.request.get('screen_name')
        # 発言者のユーザ名
        tweet.user_name = self.request.get('user_name')
        # レポート件数
        tweet.count = models.Report.all().filter('tweetid =', tweetid).count()
        # 保存
        tweet.put()
        result.append('%s=%d' % (tweetid, tweet.count))

        # 結果出力
        result = '\n'.join(result)
        self.response.headers["Content-Type"] = "text/plain"
        self.response.headers["Content-Length"] = '%d' % len(result)
        self.response.out.write(result)


class DemaCount(webapp.RequestHandler):
    """デマ件数応答"""
    def get(self):
        # ユーザ認証
        token = getToken(self.request.get('token'))
        result = ['token=%s' % token]

        # ツイートIDごとの件数
        for tweetid in self.request.get_all('tweetid'):
            tweet = models.Tweet.all().filter('tweetid =', tweetid).get()
            result.append('%s=%d' % (tweetid, tweet.count if tweet else 0))

        # 結果出力
        result = '\n'.join(result)
        self.response.headers["Content-Type"] = "text/plain"
        self.response.headers["Content-Length"] = '%d' % len(result)
        self.response.out.write(result)


def getToken(token):
    if not token:
        # 新しいトークンを発行
        token = ''.join(random.choice(string.ascii_letters) for i in range(models.User.TOKEN_LENGTH))
        models.User(token=token).put()
    return token

