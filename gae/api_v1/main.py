#!/usr/bin/env python
# coding:utf-8

from flask import Module,  render_template

v1_app = Module(__name__)

@v1_app.route('/test')
def v1_app_index():
  p = {}
  return render_template('v1/v1_index.html',  p = {}) 
