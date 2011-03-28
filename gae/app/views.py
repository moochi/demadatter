"""
Flask Module Docs:  http://flask.pocoo.org/docs/api/#flask.Module

This file is used for both the routing and logic of your
application.
"""

from flask import Module, url_for, render_template, request, redirect,\
                  session, g, flash
from flaskext.oauth import OAuth
#from models import *
import models
#from forms import TodoForm

views = Module(__name__, 'views')
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
    authorize_url='http://api.twitter.com/oauth/authenticate',
    #authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key='qbAWqQcTBtOxPqbTh5Uag',
    consumer_secret='TdKlsHpqaSzVfZircnOEoANdsylCskNsgQcvJNMqfk'
)

@twitter.tokengetter
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
 
@views.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = models.User.get_by_key_name(session['user_id'])

@views.after_request
def after_request(response):
    return response

@views.route('/')
def index():
    """Render website's index page."""
    return render_template('TopPage.html', p = {'usr': g.user})

@views.route('/mobile')
def mobile():
    if g.user is None:
        return redirect(url_for('login', next=request.url)) 
    return redirect('/static/v2/top.html')

@views.route('/login')
def login():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))


@views.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))


@views.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    """Called after authorization.  After this function finished handling,
    the OAuth information is removed from the session again.  When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.

    Because the remote application could have re-authorized the application
    it is necessary to update the values in the database.

    If the application redirected back after denying, the response passed
    to the function will be `None`.  Otherwise a dictionary with the values
    the application submitted.  Note that Twitter itself does not really
    redirect back unless the user clicks on the application name.
    """
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    #user = models.User.get_by_key_name(resp['screen_name'])
    user = models.User.get_by_key_name(resp['oauth_token'])


    # user never signed on
    if user is None:
        user = models.User.get_or_insert(key_name=resp['oauth_token'])
        user.user_id = resp['oauth_token']
        user.put()

    # in any case we update the authenciation token in the db
    # In case the user temporarily revoked access we will have
    # new tokens here.
    user.twitter_oauth_token = resp['oauth_token']
    user.twitter_oauth_secret = resp['oauth_token_secret']
    #user.screen_name = resp['screen_name']
    #user.user_name = resp['user_name']
    user.put()

    session['user_id'] = resp['oauth_token']
    flash('You were signed in')
    return redirect(next_url)

@views.app_errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


