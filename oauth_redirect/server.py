import json
import shelve

from aiohttp import ClientSession
from aiohttp import web
from aiohttp import web_exceptions as ex
from datetime import datetime, timedelta
from itertools import chain
from json import JSONDecodeError
from oauth_redirect import background
from uuid import uuid4


def is_authorized(request):
    """ Returns true if the given request has the configured auth code. """

    auth = request.match_info.get('auth')
    return auth is not None and auth == request.app.auth


def random_token():
    """ Generates random token. Uses a prefix in addition to an uuid value to
    make it easy to detect the value in a soup.

    """
    return '0x' + uuid4().hex


async def forward_request(token, request):
    """ Takes the given token and forwards the request to the associated
    redirect (must exist in database).

    Returns a web response with the same status code as the returned by
    the redirect.

    If the response was successful, the token is deleted immediately.

    """
    token_bound = request.app.db[token]
    url = token_bound['url']

    payload = await request.json(loads=quiet_json)
    payload['oauth_redirect_secret'] = token_bound['secret']

    async with ClientSession() as session:
        async with session.post(url, data=json.dumps(payload)) as response:

            if response.status == 200:
                del request.app.db[token]

            return web.Response(status=response.status)


def quiet_json(data):
    """ Parses the given json string, ignoring any parsing errors and returning
    a dictionary in any case.

    """

    try:
        return json.loads(data)
    except JSONDecodeError:
        return {}


async def extract_token(request):
    """ Takes the given request and extracts the token from it. The token
    may be stored in any formdata, json data or query field.

    Whatever is first found among query, post and json data is presumed
    to be the token.

    """

    json_data = await request.json(loads=quiet_json)
    post_data = await request.post()

    values = chain(
        request.query.values(),
        json_data.values(),
        post_data.values(),
    )

    def is_token(value):
        return value.startswith('0x') and value in request.app.db

    return next((v for v in values if is_token(v)), None)


async def receive_redirect_to(request):
    """ Receives the OAuth redirect_to response and forwards it to a registerd
    client if a match can be found.

    """
    token = await extract_token(request)

    if token:
        return await forward_request(token, request)

    raise ex.HTTPNotFound(reason="Invalid token")


async def register(request):
    """ Registers a new redirect with the server. """

    if not is_authorized(request):
        raise ex.HTTPUnauthorized()

    data = await request.json(loads=quiet_json)
    ttl = int(data.get('ttl', 3600))

    token = random_token()

    try:
        request.app.db[token] = {
            'url': data['url'],
            'expiration': datetime.utcnow() + timedelta(seconds=ttl),
            'secret': data['secret']
        }
    except KeyError as e:
        raise ex.HTTPBadRequest(reason="Missing key: {}".format(e.args[0]))

    return web.json_response({'token': token})


def create_app(database, auth):
    """ Prepares the server application. """
    app = web.Application()

    app.db = shelve.open(database)
    app.auth = auth

    app.on_startup.append(background.start_tasks)
    app.on_cleanup.append(background.cleanup_tasks)

    app.router.add_post('/redirect', receive_redirect_to)
    app.router.add_post('/register/{auth}', register)

    return app


def run_server(host, port, database, auth):
    """ Prepares and runs the server application. """
    assert auth is not None

    web.run_app(host=host, port=port, app=create_app(database, auth))