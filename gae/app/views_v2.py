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

import os, sys, codecs
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_dir, 'lib'))

from flask import Module,  render_template, session, g, redirect
from flask import make_response, Response
from flask import request
from flask import json
from twitter import get_status_by_tweet_id
import models
views_v2 = Module(__name__)

@views_v2.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = models.User.get_by_key_name(session['user_id'])

@views_v2.after_request
def after_request(response):
    return response

"""デマレポート処理"""
@views_v2.route('/api/post', methods=['GET', 'POST'])
def dema_add():
    ## ログインチェック
    if g.user is None:
        return redirect(url_for('login', next=request.url)) 
    reporter_id = session['user_id']
    flag = request.args.get('flag', type=int)
    tweet_id = request.args.get('tweet_id', type=int)
   
    ## Userオブジェクト作成
    user_obj = get_user(reporter_id)  # レポートする人のUserObject
    reporter_obj = models.Reporter(user=user_obj)
    reporter_obj.put()

    ## tweet obj作成
    twit_data =  get_status_by_tweet_id(tweet_id)

    if twit_data.has_key('text'):
      tweet_test = twit_data['text']
      import datetime
      dd = datetime.datetime.strptime(twit_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
      tweet_obj = models.Tweet.get_or_insert(key_name = str(tweet_id),
                                          tweet_id = tweet_id,
                                          tweet = twit_data['text'],
                                          screen_name = twit_data['user']['screen_name'], 
                                          user = get_user(twit_data['user']['id_str'], twit_data['user']), 
                                          lang = twit_data['user']['lang'], 
                                          tweeted_at = dd)
   
      # Reportを生成　デマレートを計算して保存
      repo = models.Report.get_or_insert(
                           key_name = "%s_%s"%(user_obj.user_id, tweet_obj.tweet_id), 
                           reporter = reporter_obj, 
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
      status = 'ok'
    else:
      status = 'ng'

    res = {'staus':status} 
    return json.dumps(res)


# デマレポート処理  ###################################################
@views_v2.route('/api/entry', methods=['GET', 'POST'])
def dema_get():
    tweet_id = request.args.get('tweet_id', type=int)
    user_obj = get_user(reporter_id)  # レポートする人のUserObject

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
    ret["status"] = "ok"
    return json.dumps(ret)


# デマランキング処理  #####################################################
@views_v2.route('/api/ranking', methods=['GET', 'POST'])
def dema_ranking():
      # TODO: ユーザ認証
      #token = getToken(self.request.get('token'))
      #result = ['token=%s' % token]

      #self.response.headers['Content-Type'] = 'application/json'

      type_str = request.args.get('type', 'rate')
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
        "tweets": [tweet_to_obj(t) for t in tweets]
        })

def tweet_to_obj(tweet):
    """ Convert tweet model to object. """
    return {"tweet_id": tweet.tweet_id,
            "text": tweet.tweet,
            "user": {
                "name": tweet.user.user_name,
                "screen_name": tweet.user.screen_name, 
                "id": tweet.user.twitter_user_id,
            },
            "dema_count": tweet.dema_count,
            "non_dema_count": tweet.non_dema_count,
            "dema_score": tweet.dema_score,
            "tweeted_at": str(tweet.get_jst()), 
           }    

#######  Utility
def get_user(user_id, user_arr=None):
    #usr = models.User.get_or_insert(key_name = user_id, user_id = user_id )
    user = models.User.get_by_key_name(user_id)

    # user never signed on
    if user is None:
        user = models.User.get_or_insert(key_name=user_id)
        user.user_id = user_id
        user.twitter_user_id = user_id
        user.screen_name = user_arr['screen_name']
        user.user_name = user_arr['name']
        user.put()
    return user


