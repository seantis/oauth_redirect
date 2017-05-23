import click

from oauth_redirect import run_server
from uuid import uuid4


@click.command()
@click.option(
    'host', '--host', '-h',
    help="The host to bind the server to",
    default='localhost')
@click.option(
    'port', '--port', '-p',
    help="The port to bind the server to",
    default=8000)
@click.option(
    'database', '--database', '-d',
    help="The database file to use",
    default='registered')
@click.option(
    'auth', '--auth', '-a',
    help="The authentication secret to use",
    default=None)
def server_cli(host, port, database, auth):
    """ Runs the oauth_redirect server. """

    if auth is None:
        auth = uuid4().hex

    print("Using the following auth secret: \n{}".format(auth))

    run_server(host, port, database, auth)
