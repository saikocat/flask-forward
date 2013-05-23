# -*- coding: utf-8 -*-

import os
import atexit
import unittest
import flask
from jinja2 import TemplateNotFound
from resolution_helper import forward_resolution, forward
from info import info


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(info)
        forward_resolution.init_app(app)
        self.app = app
        self.client = app.test_client()
        self.forward_resolution = forward_resolution

        @app.route('/no-blueprint')
        def no_blueprint():
            return forward('no_blueprint.html')

        @app.route('/no-blueprint-auto')
        def no_blueprint_auto():
            return forward()

        @app.route('/no-blueprint-custom-endpoint',
                   endpoint='no_blueprint_custom_endpoint')
        def no_blueprint_custom_endpoint_func():
            return forward()

    def tearDown(self):
        pass

    def restore_default_config(self):
        self.forward_resolution.blueprints_template_folder = ''
        self.forward_resolution.template_priority = 'Application'
        self.forward_resolution.template_extension = 'html'
        self.forward_resolution.legacy_lookup_method = False


@unittest.skip("WIP")
class SignallingTestCase(BaseTestCase):

    def test_signals(self):
        pass


class NoBlueprintTestCase(BaseTestCase):

    def test_given_template(self):
        rv = self.client.get('/no-blueprint')
        assert "Scenario: No blueprint." in rv.data

    def test_auto_template(self):
        rv = self.client.get('/no-blueprint-auto')
        assert "Scenario: No blueprint auto." in rv.data

    def test_custom_endpoint(self):
        rv = self.client.get('/no-blueprint-custom-endpoint')
        assert "Scenario: No blueprint custom endpoint." in rv.data


class BlueprintTestCase(BaseTestCase):

    def test_given_template(self):
        rv = self.client.get('/info/')
        assert "Scenario: Blueprint." in rv.data

    def test_overrided_from_flask(self):
        rv = self.client.get('/info/overrided')
        assert "Scenario: Flask Template overrided Blueprint Template." \
            in rv.data

    def test_auto_template(self):
        rv = self.client.get('/info/auto')
        assert "Scenario: Blueprint auto." in rv.data

    def test_lookup_failure(self):
        with self.assertRaises(TemplateNotFound):
            rv = self.client.get('/info/not-found-template')


class BlueprintWithConfigTestCase(BaseTestCase):

    def test_legacy_lookup_method(self):
        self.restore_default_config()
        self.forward_resolution.legacy_lookup_method = True
        rv = self.client.get('/info/', follow_redirects=True)
        assert "Scenario: Legacy lookup Blueprint." in rv.data

    def test_template_priority(self):
        self.restore_default_config()
        self.forward_resolution.template_priority = 'Blueprint'
        rv = self.client.get('/info/overrided')
        assert "Scenario: Blueprint Template overrided Flask Template." \
            in rv.data

    def test_template_priority_with_legacy(self):
        self.restore_default_config()
        self.forward_resolution.template_priority = 'Blueprint'
        self.forward_resolution.legacy_lookup_method = True
        rv = self.client.get('/info/overrided')
        assert "Scenario: Legacy lookup Blueprint with Blueprint priority." \
            in rv.data

    def test_namespaced_template_folder(self):
        self.restore_default_config()
        self.forward_resolution.blueprints_template_folder = 'namespaced'
        rv = self.client.get('/info/overrided')
        assert "Scenario: Custom Folder for Flask Template overrided " \
            "Blueprint Template." in rv.data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseTestCase))
    suite.addTest(unittest.makeSuite(NoBlueprintTestCase))
    suite.addTest(unittest.makeSuite(BlueprintTestCase))
    suite.addTest(unittest.makeSuite(BlueprintWithConfigTestCase))
    if flask.signals_available:
        suite.addTest(unittest.makeSuite(SignallingTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
