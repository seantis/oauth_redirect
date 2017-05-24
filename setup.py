# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages


if sys.hexversion < 0x03050000:
    sys.exit("Python 3.5 or newer is required to run this program.")


name = 'oauth_redirect'
description = (
    'Securely redirects OAuth responses to known clients.'
)
version = '0.3.0'


def get_long_description():
    readme = open('README.rst').read()
    history = open('HISTORY.rst').read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, history))


setup(
    name=name,
    version=version,
    description=description,
    long_description=get_long_description(),
    url='http://github.com/seantis/oauth_redirect',
    author='Seantis GmbH',
    author_email='info@seantis.ch',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=name.split('.')[:-1],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'aiohttp',
        'click',
        'purl'
    ],
    extras_require=dict(
        test=[
            'coverage',
            'mirakuru',
            'morepath',
            'pytest',
            'pytest-localserver',
            'requests',
        ],
    ),
    entry_points={
        'console_scripts': [
            'oauth-redirect = oauth_redirect.cli:server_cli'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ]
)
