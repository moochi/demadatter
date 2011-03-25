# -*- coding: utf-8 -*-

import os
from datetime import timedelta
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import models

__all__ = ('IndexaPage',)

class TemplatedPage(webapp.RequestHandler):
    """Base class for templatized handlers."""

    def write_template(self, filename, values):
        """Write out the template with the same name as the class name."""
        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(template.render(path, values))


class IndexPage(TemplatedPage):
    def get(self):
        def utc2jst(record):
            record.createdat += timedelta(hours=9)
            return record
        res = db.GqlQuery("SELECT * FROM Tweet ORDER BY count DESC LIMIT 100")
        values = {
            #'list' : models.Tweet.all(),
            'list' : map(utc2jst, res),
            }
        self.write_template('IndexPage.html', values)

