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
views_v1 = Module(__name__)

@views_v1.route('/', methods=['GET', 'POST'])
def dema_ranking
    flask.redirect('/v2/ranking')

@views_v1.route('/count', methods=['GET', 'POST'])
def dema_count
    token	= request.args.get('token')
    tweetid = request.args.get('tweetid')
    result = ['token=%s' % token]
    tweet = get_twit(tweetid)
	result.append('%s=%d' % (tweetid,tweet.dema_count))
	response = makeresponse(result)
	response['Content-Type'] = "text/plain"
	response['Content-Length'] = '%d' % len(result)
	return response

def get_twit(tweet_id):
    entity = models.Tweet.all().filter('tweet_id = ',tweet_id).get()
	return entity
