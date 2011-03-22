# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from django.utils import simplejson as json

def get_status_by_tweet_id(tweet_id):
    """ tweet_id から中身を取得。
    public な tweet のみ取得できる。

    成功時:
      {u'in_reply_to_user_id': None, 
       u'text': u'\u672c\u65e5\u5348\u524d\u307e....",
       u'created_at': u'Mon Mar 21 05:46:29 +0000 2011', 
       .....
      }

      全てのパラメータは以下の URL を参照。
      成功例: 49708434597216256
      (ref) http://dev.twitter.com/doc/get/statuses/show/:id

    エラー時:
      {u'request': u'/1/statuses/show/1.json', 
       u'error': u'No status found with that ID.'}
    """

    if type(tweet_id) is not long and type(tweet_id) is not int:
        raise ValueError('tweet id must be int or long')

    url = "http://api.twitter.com/1/statuses/show/%d.json" % tweet_id
    response = urlfetch.fetch(url)
    if response.content is not None:
        return json.loads(response.content)

    return None
