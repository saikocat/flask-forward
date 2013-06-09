=============
Flask-Forward
=============
.. currentmodule:: flask.ext.forward

Flask-Forward extension provides auto discovery, prioritization and rendering
of template for Flask based on endpoint. It is a for `render_template` so it
will take the same params as `render_template`.It is also a nice counterpart
for `redirect()`. It provides option to select template other than the default
Flask template search.

.. contents::
   :local:
   :backlinks: none


Quick Start
===========
The recommend way to use Flask-Forward is to create the forward instance
separate from the application instance or app factory module. Your blueprint
then can import the instance and use it. This also helps to avoid circular
imports.

Create a helper `resolution.py` to hold the forward instance::

    from flask.ext.forward import ForwardResolution

    forward_resolution = ForwardResolution()
    forward = forward_resolution.execute

In your blueprint say `foo_blueprint.py` and assuming it in the same path of
your `resolution.py`::

    from flask import Blueprint
    from resolution import forward

    foo = Blueprint(...)

    @foo.route('/bar')
    def show():
        return forward('bar.html', name=name)

    @foo.route('/autoforward')
    def auto():
        return forward()

Then in your `app.py` ::

    from flask import Flask

    from resolution import forward_resolution
    from foo_blueprint import foo

    app = Flask(...)

    # ... omit for brevity ...

    forward_resolution.init_app(app)

    # ... omit for brevity ...

    app.register_blueprint(foo)


Configuring your Application
============================
The most important part of an application that uses Flask-Forward is the
`ForwardResolution` class. You should create one for your application somewhere
in your code, like documented as above in `resolution.py` and wire the
attribute `forward` for later use::

    forward_resolution = ForwardResolution()
    forward = forward_resolution.execute

The forward resolution contains the code that lets your application, blueprints
and Flask-Forward work together.

Once the actual application object has been created, you can configure it for
forward with::

    forward_resolution.init_app(app)

Default config
--------------
The default NAMESPACE for Flask-Foward in `app.config` is `FORWARD`::

    'FORWARD_BLUEPRINTS_TEMPLATE_FOLDER': '',
    'FORWARD_TEMPLATE_PRIORITY': 'Application',
    'FORWARD_TEMPLATE_EXTENSION': 'html',
    'FORWARD_LEGACY_LOOKUP_METHOD': False

You can change this config prefix by specify the prefix when you call
`init_app`. For example::

    forward_resolution.init_app(app, 'FOOBAR')

This will look for config with name `FOOBAR_BLUEPRINTS_TEMPLATE_FOLDER` instead


Template Lookup Process
=======================
Let say we have a structure at root like below where `info` is a blueprint::

    info
    |---> templates
        |---> info
        |   |---> index.html
        |   |---> overrided.html
        |---> auto.html
        |---> index.html
        |---> overrided.html

    templates
    |---> info
    |   |---> overrided.html
    |---> namespaced
    |   |---> info
    |       |---> overrided.html
    |---> no_blueprint.html
    |---> no_blueprint_auto.html
    |---> no_blueprint_custom_endpoint.html

Info blueprint views::

    @info.route('/', defaults={'page': 'index'})
    @info.route('/<page>')
    def show(page):
        return forward('%s.html' % page)

    @info.route('/auto')
    def auto():
        return forward()

For non-blueprints forwarding and default configurations

- Forward with template argument::

    # Template: 'templates/no_blueprint.html'
    @app.route('/no-blueprint')
    def no_blueprint():
        return forward('no_blueprint.html')

- Forward without template argument (auto discovery)::

    # Template: 'templates/no_blueprint_auto.html'
    @app.route('/no-blueprint-auto')
    def no_blueprint_auto():
        return forward()

- Forward without template argument (auto discovery) but with custom endpoint::

    # Template: 'templates/no_blueprint_custom_endpoint.html'
    @app.route('/no-blueprint-custom-endpoint',
               endpoint='no_blueprint_custom_endpoint')
    def no_blueprint_custom_endpoint_func():
        return forward()

For blueprint forwarding and default configurations

`/info/`
    Template `info/templates/index.html` will be returned

`/info/overrided`
    By default we respect Flask App template priority. So app-wide template
    `templates/info/overrided.html` is chosen over blueprint template
    `info/templates/overrided.html`.

`/info/auto`
    Auto template discovery will return `info/templates/auto.html`

`/info/not-found`
    Raise **TemplateNotFound** exception


Customizing the Template Lookup process
=======================================

Legacy Lookup Method
--------------------
If you want to use legacy lookup method (for a lack of better name)  or the
default Flask look up method for blueprints
(http://flask.pocoo.org/docs/blueprints/#templates). You can enable this
option by settomg in the app config or update the forward property::

    # before calling init_app
    app.config['FORWARD_LEGACY_LOOKUP_METHOD'] = True

    # or after calling init_app
    forward_resolution.legacy_lookup_method = True

`/info/`
    Template `info/templates/info/index.html` is returned. Notice the extra
    `info` subfolder.


Blueprint Priority
------------------
If you want to always prefer the blueprint template over the app wide template::

    # before calling init_app
    app.config['FORWARD_TEMPLATE_PRIORITY'] = 'Blueprint'

    # or after calling init_app
    forward_resolution.template_priority = 'Blueprint'

`/info/overrided`
    Template `info/templates/overrided.html` is used instead of
    `templates/info/overrided.html`

Blueprint Priority with Legacy Lookup
-------------------------------------
When combining the 2 options above, when we access

`/info/overrided`
    Template `info/templates/info/overrided.html` is returned


Specific Folder for Blueprint Templates
---------------------------------------
If you want to namespace your blueprint templates folder further in the app
wide Flask template folder::

    # before calling init_app
    app.config['FORWARD_BLUEPRINTS_TEMPLATE_FOLDER'] = 'namespaced'

    # or after calling init_app
    forward_resolution.blueprints_template_folder = 'namespaced'

`/info/overrided`
    Template `templates/namespaced/info/overrided.html` is returned

Note: Try not to use this option with legacy lookup option :(

API Documentation
=================
This documentation is automatically generated from Flask-Forward's source code.
WIP


TODO
====
- Use Generator for lazy load of template loader
- Add a proxy object for forward resolution
- Auto conversion of dash into underscore option from endpoint to template
  ('/foo-bar' -> 'templates/foo_bar.html')
- Swappable rendering engine
- Signals
- API Documentation
