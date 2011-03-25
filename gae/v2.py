#!/usr/bin/env python
# coding:utf-8

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from pages import IndexPage
from api_v2 import *

urlmap = (
           # エントリ投稿系
           ('/v2/api/post',  DemaAdd),
           #('/v2/api/post/(.*)',  DemaAdd),
           # エントリ情報取得 
           ('/v2/api/entry',  DemaGet),
           # ランキング取得系
           ('/v2/api/ranking', DemaRanking),
         )


def main():
    application = webapp.WSGIApplication(urlmap, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()


