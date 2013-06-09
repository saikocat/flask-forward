# -*- coding: utf-8 -*-
"""
    flask.ext.forward
    ~~~~~~~~~~~~~~~~~

    This module provides auto discovery, prioritization and rendering of
    template for Flask application.

    :copyright: (C) 2013 by Nguyen Duc Hoa.
    :license: MIT/X11, see LICENSE for more details.
"""

import os
from collections import OrderedDict
from flask import _app_ctx_stack, _request_ctx_stack, request
from flask.signals import Namespace
from flask.templating import render_template
from werkzeug.local import LocalProxy
from jinja2 import FileSystemLoader, TemplateNotFound

connection_stack = _app_ctx_stack or _request_ctx_stack

_signals = Namespace()

_forward = LocalProxy(lambda: current_app.extensions['forward'])

_default_config = {
    'BLUEPRINTS_TEMPLATE_FOLDER': '',
    'TEMPLATE_PRIORITY': 'Application',
    'TEMPLATE_EXTENSION': 'html',
    'LEGACY_LOOKUP_METHOD': False
}


class ForwardResolution(object):
    """The :class:`ForwardResolution` class initializes the Flask-Forward
     extension.

    :param app: The application.
    :param config_prefix: The prefix namespace for config keys
    """
    def __init__(self, app=None, config_prefix='FORWARD'):
        if app is not None:
            self.app = app
            self.init_app(self.app, config_prefix)
        else:
            self.app = None

    def init_app(self, app, config_prefix='FORWARD'):
        self.config_prefix = config_prefix

        for key, value in _default_config.items():
            config_key = '{0}_{1}'.format(self.config_prefix, key)
            app.config.setdefault(config_key, value)
            setattr(self, key.lower(), app.config[config_key])

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['forward'] = self

    def get_app(self):
        if self.app is not None:
            return self.app
        ctx = connection_stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application is not registered')

    def execute(self, template=None, **kwargs):
        result_template = self.guess_template(template)

        return render_template(result_template, **kwargs)

    def guess_template(self, template_name):
        app = self.get_app()
        ctx = _request_ctx_stack.top
        request = ctx.request
        request_blueprint = request.blueprint
        result_template = template_name

        blueprint = app.blueprints[request_blueprint] \
            if request_blueprint is not None else None

        if result_template is None:
            result_template = request.endpoint.replace('.', '/') + '.' + \
                self.template_extension

        if blueprint is not None:
            result_template = self.blueprint_template_lookup(blueprint,
                                                             result_template)
        return result_template

    def blueprint_template_lookup(self,
                                  blueprint, template_name):
        app = self.get_app()
        jinja_env = app.jinja_env
        default_template_loader = jinja_env.loader
        result_template = None

        loaders_templates = self.get_loaders_and_templates(blueprint,
                                                           template_name)
        for loader, template in loaders_templates.items():
            try:
                jinja_env.loader = loader
                result_template = jinja_env.get_template(template)
                break
            except TemplateNotFound:
                result_template = None
                continue

        # Reset the jinja env loader
        app.jinja_env.loader = default_template_loader

        if result_template is None:
            raise TemplateNotFound(template_name)

        return result_template

    def get_loaders_and_templates(self, blueprint, template_name):
        loaders_templates = OrderedDict()
        default_searchpath = list(self.get_app().jinja_loader.searchpath)
        app_template_path = self.get_app_template_path(blueprint,
                                                       template_name)
        app_jinja_loader = FileSystemLoader(default_searchpath)

        blueprint_template_path = self.get_blueprint_template_path(
            blueprint, template_name)
        blueprint_jinja_loader = blueprint.jinja_loader

        loader_pairs = [{app_jinja_loader: app_template_path},
                        {blueprint_jinja_loader: blueprint_template_path}]

        if self.template_priority.lower() == 'application':
            pass
        elif self.template_priority.lower() == 'blueprint':
            loader_pairs.reverse()

        for pair in loader_pairs:
            for loader, template in pair.items():
                loaders_templates[loader] = template

        return loaders_templates

    def get_app_template_path(self, blueprint, template_name):
        return self.blueprints_template_folder + '/' + blueprint.name + '/' + \
            template_name

    def get_blueprint_template_path(self, blueprint, template_name):
        if self.legacy_lookup_method is True:
            template_path = blueprint.name + '/' + template_name
        else:
            template_path = template_name.replace(blueprint.name, '', 1)
        return template_path
