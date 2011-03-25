#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import urllib
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class TemplatedPage(webapp.RequestHandler):
  """Base class for templatized handlers."""
  
  def write_template(self, values):
    """Write out the template with the same name as the class name."""
    path = os.path.join(os.path.dirname(__file__), 'templates',
                        self.__class__.__name__ + '.html')
    self.response.out.write(template.render(path, values))


class TopPage(TemplatedPage):
    def get(self):
        # self.response.out.write('Hello world2!')
        values = {
            'title': 'App Engine Image Demo'
        }
        self.write_template(values)


def main():
    application = webapp.WSGIApplication([('/', TopPage)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
