# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from flask import g,session
from django.utils import simplejson as json
from flaskext.oauth import OAuth
import logging

def get_twitter_obj():
    oauth = OAuth()
    twitter = oauth.remote_app('twitter',
        base_url='http://api.twitter.com/1/',
        # where flask should look for new request tokens
        request_token_url='http://api.twitter.com/oauth/request_token',
        # where flask should exchange the token with the remote application
        access_token_url='http://api.twitter.com/oauth/access_token',
        # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
        # they mostly work the same, but for sign on /authenticate is
        # expected because this will give the user a slightly different
        # user interface on the twitter side.
        #authorize_url='http://api.twitter.com/oauth/authenticate',
        authorize_url='https://api.twitter.com/oauth/authorize',
        consumer_key='qbAWqQcTBtOxPqbTh5Uag',
        consumer_secret='TdKlsHpqaSzVfZircnOEoANdsylCskNsgQcvJNMqfk'
    )
    twitter.tokengetter(get_twitter_token)
    return twitter

def get_twitter_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls.  During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    user = g.user
    if user is not None:
        return user.twitter_oauth_token, user.twitter_oauth_secret
 

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

    twitter = get_twitter_obj()
    url = "statuses/show/%d.json" % tweet_id
    response = twitter.get(url)
    #response = urlfetch.fetch(url)
    if response.status == 200:
        return response.data
    else:
        return None

if __name__ == '__main__':
  sample_tweet_id = 53390888138846208
  print get_status_by_tweet_id(sample_tweet_id)


'''
Tweetに埋めこまれているUser情報
user: {
  profile_sidebar_border_color: "2F5D69"
  default_profile_image: false
  description: "wave班 http://twilog.org/atusibrあつし or atusi "
  location: "港区,  東京都 JP"
  lang: "ja"
  profile_use_background_image: true
  profile_background_color: "FFFFFF"
  show_all_inline_media: true
  follow_request_sent: false
  profile_background_image_url: "http://a3.twimg.com/profile_background_images/22076832/_____1.png"
  is_translator: false
  geo_enabled: true
  created_at: "Mon Apr 09 18:54:08 +0000 2007"
  default_profile: false
  statuses_count: 16978
  time_zone: "Tokyo"
  profile_text_color: "374C64"
  contributors_enabled: false
  following: true
  friends_count: 1028
  profile_sidebar_fill_color: "CCF3F3"
  followers_count: 1436
  protected: false
  id_str: "3933331"
  listed_count: 119
  profile_background_tile: false
  favourites_count: 76
  profile_image_url: "http://a3.twimg.com/profile_images/500679931/a2c_meca_normal.jpg"
  name: "a2c"
  id: 3933331
  verified: false
  notifications: false
  utc_offset: 32400
  profile_link_color: "C300CB"
  url: "http://d.hatena.ne.jp/a2c/"
  screen_name: "atusi"
}
'''

