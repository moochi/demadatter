#!/usr/bin/env python
# coding:utf-8

import string
import random
from datetime import datetime

from django.utils import simplejson as json
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import models
from twitter import get_status_by_tweet_id
import logging



class DemaAdd(webapp.RequestHandler):
    """デマレポート処理"""
    def get(self):
        tweet_id  = int(self.request.get('tweet_id'))
        reporter_id = self.request.get('reporter_id')
        reporter_id  = '1'

        flag = int(self.request.get('flag'))

        logging.info(tweet_id)
        twit_data =  get_status_by_tweet_id(tweet_id)

        ## Tweetを作る
        tweet = twit_data[u'text']  # twit の本文
        user_obj = get_user(reporter_id)  # レポートする人のUserObject
        tweet_obj = save_create_twit(
                     tweet_id   = tweet_id, 
                     tweet      = tweet, 
                     user       = user_obj, 
                     tweeted_at = twit_data['created_at']
                     )

        ## Reportを作る
        repo = models.Report.get_or_insert(
                             key_name = "%s_%s"%(user_obj.user_id, tweet_obj.tweet_id), 
                             reporter = user_obj, 
                             tweet = tweet_obj, 
                             )
        
        before_flag = repo.dema_flag
        repo.dema_flag = flag
        dema_delta = [0, 0]

        if before_flag == 1:
             dema_delta[0] -= 1
        elif before_flag == -1:
             dema_delta[1] -= 1

        if flag == 1:
             dema_delta[0] += 1
        elif flag == -1:
             dema_delta[1] += 1

        tweet_obj.set_dema_cnt(*dema_delta)
        tweet_obj.put()
         
        repo.put()
        res = {'staus':'ok'} 
        #res_json = json.dumps(res, indent=1, ensure_ascii=False)
        res_json = json.dumps(res)
        self.response.out.write(res_json)
        
    def post(self):
        # return demo data
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("""{"status": "success"}""")
        return

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


class DemaGet(webapp.RequestHandler):
    """デマレポート処理"""
    def get(self):
        tweet_id = int(self.request.get('tweet_id'))

        self.response.headers['Content-Type'] = 'application/json'
        try:
            if self.request.get('demo'):
                self.show_demo_tweet(tweet_id)
            else:
                self.show_tweet(tweet_id)
        except Exception, e:
            self.response.set_status(500)
            self.response.out.write(json.dumps({
                "status": "ng", 
                "text": "Internal Server Error",
                "detail": str(e),
            }))

    def show_tweet(self, tweet_id):
        """ Show datastore data. """
        tweet = models.Tweet.get_by_key_name(str(tweet_id))
        if tweet is None:
            self.response.set_status(404)
            self.response.out.write('{ "status": "ng", "text": "Not Found"}')
            return

        ret = tweet_to_obj(tweet)
        ret["status"] = "success"
        self.response.out.write(json.dumps(ret))

    def show_demo_tweet(self, tweet_id):
        """ Show demo data. """
        self.response.out.write("""
{"status": "success",
 "tweet_id": %d,
 "text": "東電に勤めてる知り合いによると、いま放射能が大量に出てきて作業している人が逃げ出したらしい",
 "user": {
     "name": "nitoyon",
     "id": 12345,
     "screen_name": "nitoyon",
     "followers_count": 28
 },
 "dema_count": 3,
 "non_dema_count": 2,
 "dema_score": 0.6
}""" % tweet_id)


class DemaCount(webapp.RequestHandler):
    def get(self):
        # ユーザ認証
        token = getToken(self.request.get('token'))
        result = ['token=%s' % token]


class DemaRanking(webapp.RequestHandler):
    """デマランキング応答"""
    def get(self):
        # TODO: ユーザ認証
        #token = getToken(self.request.get('token'))
        #result = ['token=%s' % token]

        self.response.headers['Content-Type'] = 'application/json'

        type_str = self.request.get('type', 'rate')
        if type_str not in ["rate", "date"]:
            self.response.out.write('{"status": "ng", "text": "invalid type" }')
            return

        try:
            if self.request.get('demo'):
                self.show_demo_rank(type_str)
            else:
                self.show_rank(type_str)
        except Exception, e:
            self.response.set_status(500)
            self.response.out.write(json.dumps({
                "status": "ng", 
                "text": "Internal Server Error",
                "detail": str(e),
            }))

    def show_rank(self, type_str):
        if type_str == 'date':
            order_column = '-created_at'
        else:
            order_column = '-dema_score'
        tweets = models.Tweet.all().order(order_column).fetch(30)
        self.response.out.write(json.dumps({
            "status": "success", 
            "type": type_str,
            "tweets": [tweet_to_obj(t) for t in tweets]
        }))

    def show_demo_rank(self, type_str):
        self.response.out.write("""{
 "status": "success",
 "type": "%s",
 "tweets": [
   {
     "tweet_id": 1234,
     "text": "東電に勤めてる知り合いによると、いま放射能が大量に出てきて作業している人が逃げ出したらしい",
     "user": {
         "name": "nitoyon",
         "id": 12345,
         "screen_name": "nitoyon",
         "followers_count": 28
     },
     "dema_count": 3,
     "non_dema_count": 2,
     "dema_score": 0.6
   }
 ]
}""" % str(type_str))


##  Utility
def save_create_twit(tweet_id, tweet, user,tweeted_at):
    u"""
    tweet_id : Tweet ID
    tweet : Tweet 本文
    user : 投稿者のUserエンティティ
    """
    import datetime
    print tweeted_at
    dd = datetime.datetime.strptime(tweeted_at, '%a %b %d %H:%M:%S +0000 %Y')
    entity = models.Tweet.get_or_insert(key_name = str(tweet_id),
                                        tweet_id = tweet_id,
                                        tweet = tweet,
                                        user = user, 
                                        tweeted_at = dd)
    return entity
    

def tweet_to_obj(tweet):
    """ Convert tweet model to object. """
    return {"tweet_id": tweet.tweet_id,
            "text": tweet.tweet,
            "user": {
                "name": "nitoyon",#tweet.user.name,
                "screen_name": "nitoyon",#tweet.user.screen_name
                "id": 1,
            },
            "dema_count": tweet.dema_count,
            "non_dema_count": tweet.non_dema_count,
            "dema_score": tweet.dema_score,
           }

def getToken(token):
    if not token:
        # 新しいトークンを発行
        token = ''.join(random.choice(string.ascii_letters) for i in range(models.User.TOKEN_LENGTH))
        models.User(token=token).put()
    return token


def get_user(user_id):
    usr = models.User.get_or_insert(key_name = str(user_id), user_id = int(user_id) )
    return usr
