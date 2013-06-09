# -*- coding: utf-8 -*-

"""
Flask-Forward
----------------

Flask-Forward provides auto discovery, prioritization and rendering of template
for Flask application.

Links
`````

* `documentation <http://packages.python.org/Flask-Forward>`_
* `development version
  <http://github.com/saikocat/flask-forward>`_

"""
from setuptools import setup


setup(
    name='Flask-Forward',
    version='0.1.0',
    url='https://github.com/saikocat/flask-forward',
    license='MIT',
    author='Nguyen Duc Hoa',
    author_email='hoameomu@gmail.com',
    description='Flask-Forward extension provides auto discovery, \
                 prioritization and rendering of template for Flask \
                 based on endpoint',
    long_description=__doc__,
    py_modules=['flask_forward'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'setuptools',
        'Flask'
    ],
    test_suite='tests.test_forward.suite',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
