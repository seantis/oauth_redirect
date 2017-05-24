oauth_redirect
==============

Securely redirects OAuth responses to known clients.

Description
-----------

During the OAuth workflow a webserver defined by redirect_uri receives the
result of a the authorization given by the enduser.

This redirect_uri is usually a whitelisted uri to avoid phising attacks.

Unfortunately this makes it hard to write an OAuth integrated client to an
API where the domain is not known in advance.

Faced with such a situation we wrote this server to move the decision of
who can receive the result of an OAuth handshake from the OAuth provider
to an intermediary.

How it Works
------------

Using oauth_redirect the OAuth workflow works as follows:

1. The oauth_redirect server is run on a TLS protected site. For example:
   https://oauth.seantis.ch.

2. The OAuth provider is configured to allow redirects to
   https://oauth.seantis.ch/redirect.

3. The client that wants to acquire the authorisation registers itself with
   the oauth_redirect server using a secret authentication code.

4. The enduser is presented with the OAuth authorization site, with the
   redirect_uri set to https://oauth.seantis.ch/redirect.

5. The result is sent to the oauth_redirect server, which will forward/proxy
   the request to the client, if and only if the client has registered itself
   before and the request from the OAuth provider contains a token to that
   effect.

Methods
-------

``POST /register/<authentication code>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used by the client/authorisation seeker to register itself. The client is
required to include a secret authentication code in the registration message.

The body of the POST request is a json in this form::

    {
        'url': "The url that handles the forwarded OAuth response.",
        'method': "The method with which the url should be called (get, put or post).",
        'success_url': "The url the server redirects to if the handler url returns a 2XX code.",
        'error_url': "The url the server redirects to if the handler url returns a non-2XX code.",
        'ttl': "The optional time to live in seconds (defaults to 3600 seconds)",
        'secret': "A client-specific secret that should be used authenticate
        the forwarded request. If the request does not contain this secret,
        someone other than oauth_redirect has sent it.",
    }

Returns the token which needs to be passed by the OAuth provider::

    {
        'token': "..."
    }

``(GET|POST) /redirect``
~~~~~~~~~~~~~~~~~~~~~~~~

The endpoint communicated to the OAuth provider through the redirect_uri. To
authenticate the request coming from the OAuth provider must contain the
token given by ``/register/<authentication code>``.

Usually OAuth providers provide some kind of of value that may be passed from
the client to the redirect_uri. This value can be used to carry the token
back to the oauth_redirect server.

If there is no such value, the token may also be passed by url, using query
paramters (i.e. https://oauth.seantis.ch/redirect?token=...).

Any value will do, a value in a json body, a formdata value or a query
parameter.

If the redirect request is accepted it is proxied to the registered url. The
result of the ``/redirect`` request is the result of the proxied url.

If the request was accepted, it is deleted.

Deployment
----------

The server is implemented using `aiohttp <http://aiohttp.readthedocs.io/en/stable/>`_.
It requires at least Python 3.5.

Though it might be possible to implement TLS support on the oauth_redirect we
recommend that you put it behind a proper web proxy like nginx/apache.

To run the server run::

    oauth-redirect --host localhost --port 8080 --database registered --auth <your custom auth code>


Run the Tests
-------------

Install tox and run it::

    pip install tox
    tox

Limit the tests to a specific python version::

    tox -e py27

Conventions
-----------

Oauth_redirect follows PEP8 as close as possible. To test for it run::

    tox -e pep8

Oauth_redirect uses `Semantic Versioning <http://semver.org/>`_

Build Status
------------

.. image:: https://travis-ci.org/seantis/oauth_redirect.png
  :target: https://travis-ci.org/seantis/oauth_redirect
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/seantis/oauth_redirect/badge.png?branch=master
  :target: https://coveralls.io/r/seantis/oauth_redirect?branch=master
  :alt: Project Coverage

Latest PyPI Release
-------------------

.. image:: https://badge.fury.io/py/oauth_redirect.svg
    :target: https://badge.fury.io/py/oauth_redirect
    :alt: Latest PyPI Release

License
-------
oauth_redirect is released under GPLv2
