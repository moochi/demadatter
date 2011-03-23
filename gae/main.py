# coding: UTF-8

import settings
from wsgiref.handlers import CGIHandler
from google.appengine.ext.appstats import recording
import sys, os

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root_dir, 'lib'))

from flask import Flask
app = Flask(__name__)
app.config.from_object('settings')

from flask import g
from flask import redirect
from flask import url_for
from flask import session
from flask import request
from flask import render_template
from flask import abort
from flask import flash
from flask import get_flashed_messages
from flask import json

from decorators import login_required, cache_page

from models import User

from gaeUtils.util import generate_key
from google.appengine.api.labs import taskqueue

@app.before_request
def before_request():
    """
    if the session includes a user_key it will also try to fetch
    the user's object from memcache (or the datastore).
    if this succeeds, the user object is also added to g.
    """
    if 'user_key' in session:
        user = cache.get(session['user_key'])

        if user is None:
            # if the user is not available in memcache we fetch
            # it from the datastore
            user = User.get_by_key_name(session['user_key'])

            if user:
                # add the user object to memcache so we
                # don't need to hit the datastore next time
                cache.set(session['user_key'], user)

        g.user = user
    else:
        g.user = None

@app.route('/')
def index():
    return render_template('TopPage.html')


from api_v1.main import v1_app
app.register_module(v1_app,  url_prefix='/v1')

from api_v2.main import v2_app
app.register_module(v2_app,  url_prefix='/v2')

_debugged_app = None
if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    # use our debug.utils with Jinja2 templates
    import debug.utils
    sys.modules['werkzeug.debug.utils'] = debug.utils

    # don't use inspect.getsourcefile because the imp module is empty
    import inspect
    inspect.getsourcefile = inspect.getfile

    # wrap the application
    from werkzeug import DebuggedApplication
    if _debugged_app is None:
        _debugged_app = app = DebuggedApplication(app, evalex=True)
    else:
        app = _debugged_app             
#app = DebuggedApplication(app, evalex=True)

CGIHandler().run(recording.appstats_wsgi_middleware(app))

