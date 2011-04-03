# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from django.utils import simplejson as json
import logging

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
        data = json.loads(response.content)
        if data.has_key('text'):
          logging.info(data['text'])
        else:
          logging.info('data has no text elements')
          logging.info(str(response.content))
        return json.loads(response.content)

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

