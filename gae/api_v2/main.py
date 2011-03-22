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

from flask import Module,  render_template
from flask import make_response, Response
from flask import request
from flask import json
import logging
from twitter import get_status_by_tweet_id
import models
v2_app = Module(__name__)

"""デマレポート処理"""
@v2_app.route('/api/post/<int:flag>/<int:reporter_id>/<int:tweet_id>',
              methods=['GET', 'POST'])
def dema_add(flag, reporter_id, tweet_id):
    reporter_id  = '1'
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
    return res_json


# デマレポート処理
#@v2_app.route('/api/entry/<tweet_id_arg>')
@v2_app.route('/api/entry/<tweet_id_arg>', methods=['GET', 'POST'])
def dema_get(tweet_id_arg):
    #tweet_id = int(request.form['tweet_id'])
    tweet_id = int(tweet_id_arg)

    #Response(headers)['Content-Type'] = 'application/json'
    try:
        return show_tweet(tweet_id)
    except Exception, e:
        res = json.dumps({
              "status": "ng", 
              "text": "Internal Server Error",
              "detail": str(e),
            })
        #Response.status_code = 500
        return res


def show_tweet(tweet_id):
    """ Show datastore data. """
    tweet = models.Tweet.get_by_key_name(str(tweet_id))
    if tweet is None:
        return json.dumps({ "status": "ng", "text": "Not Found"})
    ret = tweet_to_obj(tweet)
    ret["status"] = "success"
    return json.dumps(ret)


# デマレポート処理
@v2_app.route('/api/ranking/<type>', methods=['GET', 'POST'])
def dema_ranking(type):
      # TODO: ユーザ認証
      #token = getToken(self.request.get('token'))
      #result = ['token=%s' % token]

      #self.response.headers['Content-Type'] = 'application/json'

      #type_str = self.request.get('type', 'rate')
      #type_str = request.form['type', 'rate']
      #type_str = request.form['type']
      type_str = type
      if type_str not in ["rate", "date"]:
          return json.dumps({"status": "ng", "text": "invalid type" })
      try:
          return show_rank(type_str)
      except Exception, e:
          #self.response.set_status(500)
          return json.dumps({
              "status": "ng", 
              "text": "Internal Server Error",
              "detail": str(e)
               })

def show_rank(type_str):
    if type_str == 'date':
        order_column = '-created_at'
    else:
        order_column  = '-dema_score'
    tweets = models.Tweet.all().order(order_column).fetch(30)
    return json.dumps({
        "statuss":"success", 
        "type": type_str,
        "tw": [tweet_to_obj(t) for t in tweets]
        })


#######  Utility
def save_create_twit(tweet_id, tweet, user,tweeted_at):
    u"""
    tweet_id : Tweet ID
    tweet : Tweet 本文
    user : 投稿者のUserエンティティ
    """
    import datetime
    #print tweeted_at
    dd = datetime.datetime.strptime(tweeted_at, '%a %b %d %H:%M:%S +0000 %Y')
    entity = models.Tweet.get_or_insert(key_name = str(tweet_id),
                                        tweet_id = tweet_id,
                                        tweet = tweet,
                                        user = user, 
                                        tweeted_at = dd)
    return entity   
    

def get_user(user_id):
    usr = models.User.get_or_insert(key_name = str(user_id), user_id = int(user_id) )
    return usr

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


