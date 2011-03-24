"""
Flask Module Docs:  http://flask.pocoo.org/docs/api/#flask.Module

This file is used for both the routing and logic of your
application.
"""

from flask import Module, url_for, render_template, request, redirect
from models import Todo
from forms import TodoForm

views = Module(__name__, 'views')


@views.route('/')
def index():
    """Render website's index page."""
    return render_template('TopPage.html')

@views.app_errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
