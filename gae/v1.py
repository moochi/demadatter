# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from pages import IndexPage
from api_v1 import DemaAdd, DemaCount

urlmap = (
           ('/v1/',     IndexPage),
           ('/v1/add',  DemaAdd),
           ('/v1/count',DemaCount),
         )


def main():
    application = webapp.WSGIApplication(urlmap, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

