import morepath
import pytest
import tempfile

from mirakuru import TCPExecutor
from pathlib import Path
from pytest_localserver.http import WSGIServer
from uuid import uuid4


def create_wsgi_endpoint_app(output_path):

    class App(morepath.App):
        pass

    @App.path('/')
    class Endpoint(object):
        pass

    @App.view(model=Endpoint, request_method='POST')
    def view_endpoint(self, request):
        with (output_path / 'request.json').open('w') as f:
            f.write(request.text)

    return App()


@pytest.fixture(scope='module')
def temporary_path():
    with tempfile.TemporaryDirectory() as tempdir:
        yield Path(tempdir)


@pytest.fixture(scope='module')
def json_endpoint(temporary_path):
    server = WSGIServer(application=create_wsgi_endpoint_app(temporary_path))
    server.start()
    server.temporary_path = temporary_path

    yield server

    server.stop()


@pytest.fixture(scope='module')
def oauth_redirect_server(temporary_path):
    config = temporary_path / 'config.yml'
    database = temporary_path / 'registered_clients'
    auth = uuid4().hex

    with config.open('w') as f:
        f.write('\n'.join((
            'database: {}'.format(database),
            'auth: {}'.format(auth)
        )))

    command = 'oauth-redirect -h 127.0.0.1 -p 8000 -a {} -d {}'.format(
        auth, database
    )

    server = TCPExecutor(command, host='127.0.0.1', port=8000, shell=True)
    server.start()
    server.config = config
    server.database = database
    server.auth = auth
    server.url = 'http://127.0.0.1:8000'

    yield server

    server.stop()
