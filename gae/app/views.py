"""
Flask Module Docs:  http://flask.pocoo.org/docs/api/#flask.Module

This file is used for both the routing and logic of your
application.
"""

from flask import Module, url_for, render_template, request, redirect,\
                  session, g, flash
from flaskext.oauth import OAuth
import models
import hashlib
from forms import TodoForm
from twitter import get_twitter_obj

views = Module(__name__, 'views')
twitter = get_twitter_obj()


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
    return redirect('/static/v2/top.html')

@views.route('/login')
def login(next=''):
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    resp=request.args.get('next') or request.referrer or None
    return twitter.authorize(callback=url_for('oauth_authorized', next=resp))


@views.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))


#@views.route('/setting')
#def setting():
    #if g.user is None:
        #return redirect(url_for('login', next=request.url)) 
    #return render_template('TopPage.html', p = {'usr': g.user})
    ##return render_template('TopPage.html', p = {'usr': g.user})


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

    user = models.User.get_by_key_name(resp['user_id'])

    # user never signed on
    if user is None:
        user = models.User.get_or_insert(key_name=resp['user_id'])
        user.user_id = resp['user_id']
        user.put()

    # in any case we update the authenciation token in the db
    # In case the user temporarily revoked access we will have
    # new tokens here.
    user.user_id = resp['user_id']
    user.token = make_session_key(resp['user_id'])
    user.twitter_user_id = resp['user_id']
    user.screen_name = resp['screen_name']

    user.twitter_oauth_token = resp['oauth_token']
    user.twitter_oauth_secret = resp['oauth_token_secret']
    user.set_session_token()
    user.put()

    session['user_id'] = user.user_id
    flash('You were signed in')
    return redirect(next_url)

@views.app_errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


def make_session_key(keyID):
    base_token = str(keyID) + 'demadatter'
    return hashlib.sha1(base_token).hexdigest()
