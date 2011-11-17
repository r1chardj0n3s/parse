#! /usr/bin/env python

from distutils.core import setup

from html import __version__, __doc__

# perform the setup action
setup(
    name = "html",
    version = __version__,
    description = "simple, elegant HTML, XHTML and XML generation",
    long_description = __doc__.decode('utf8'),
    author = "Richard Jones",
    author_email = "rjones@ekit-inc.com",
    py_modules = ['html'],
    url = 'http://pypi.python.org/pypi/html',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: BSD License',
    ],
)

# vim: set filetype=python ts=4 sw=4 et si
