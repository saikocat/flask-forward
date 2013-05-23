# -*- coding: utf-8 -*-

from flask.views import MethodView

from . import info
from ..resolution_helper import forward_resolution, forward


@info.route('/', defaults={'page': 'index'})
@info.route('/<page>')
def show(page):
    return forward('%s.html' % page)


@info.route('/auto')
def auto():
    return forward()

# custom endpoint
