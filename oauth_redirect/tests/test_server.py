import json
import pytest
import requests
import time


def test_unauthorized(oauth_redirect_server):
    url = oauth_redirect_server.url

    assert requests.post('{}/register'.format(url)).status_code == 404
    assert requests.post('{}/register/foobar'.format(url)).status_code == 401


def test_unknown_oauth_request(oauth_redirect_server):
    url = '{}/redirect'.format(oauth_redirect_server.url)

    assert requests.post(url).status_code == 404
    assert requests.post(url, json={'state': '0xunknown'}).status_code == 404


def test_end_to_end(oauth_redirect_server, json_endpoint):
    register = '{}/register/{}'.format(
        oauth_redirect_server.url, oauth_redirect_server.auth)

    redirect = '{}/redirect'.format(
        oauth_redirect_server.url)

    # run the whole thing end-to-end
    response = requests.post(register, json={
        'url': json_endpoint.url,
        'secret': "Area 51",
        'method': "POST",
        'success_url': 'http://example.org',
        'error_url': 'http://example.org'
    })

    assert response.status_code == 200
    data = response.json()

    assert 'token' in data
    assert data['token'].startswith('0x')

    response = requests.post(redirect, json={
        'foo': 'bar',
        'bar': data['token']
    }, allow_redirects=False)

    assert response.status_code == 302

    with (json_endpoint.temporary_path / 'POST.json').open('r') as f:
        received = json.loads(f.read())

    assert received['foo'] == 'bar'
    assert received['bar'] == data['token']
    assert received['oauth_redirect_secret'] == "Area 51"

    # try to repeat the request using the same code
    assert requests.post(redirect, json={
        'foo': 'bar',
        'bar': data['token']
    }).status_code == 404

    # try to send a request after it's expiry has been reached
    response = requests.post(register, json={
        'url': json_endpoint.url,
        'ttl': 1,
        'secret': "Area 51",
        'method': "POST",
        'success_url': 'http://example.org',
        'error_url': 'http://example.org'
    })
    data = response.json()

    time.sleep(2)

    assert requests.post(redirect, json={
        'foo': 'bar',
        'bar': data['token']
    }).status_code == 404


@pytest.mark.parametrize('method', [
    'GET',
    'PUT',
    'POST'
])
def test_request_methods(oauth_redirect_server, json_endpoint, method):
    register = '{}/register/{}'.format(
        oauth_redirect_server.url, oauth_redirect_server.auth)

    redirect = '{}/redirect'.format(
        oauth_redirect_server.url)

    # simulate oauth provider that sends post
    response = requests.post(register, json={
        'url': json_endpoint.url,
        'secret': "Area 51",
        'method': method,
        'success_url': 'http://example.org',
        'error_url': 'http://example.org',
    })

    token = response.json()['token']

    response = requests.post(redirect, json={
        'foo': 'bar',
        'bar': token
    }, allow_redirects=False)

    assert response.status_code == 302

    result = json_endpoint.temporary_path / '{}.json'.format(method)
    with (result).open('r') as f:
        received = json.loads(f.read())

    assert received['foo'] == 'bar'
    assert received['bar'] == token
    assert received['oauth_redirect_secret'] == "Area 51"

    # simulate oauth provider that sends get
    response = requests.post(register, json={
        'url': json_endpoint.url,
        'secret': "Area 51",
        'method': method,
        'success_url': 'http://example.org',
        'error_url': 'http://example.org',
    })

    token = response.json()['token']

    response = requests.get(
        redirect + '?foo=bar&bar=' + token,
        allow_redirects=False
    )
    assert response.status_code == 302

    result = json_endpoint.temporary_path / '{}.json'.format(method)
    with (result).open('r') as f:
        received = json.loads(f.read())

    assert received['foo'] == 'bar'
    assert received['bar'] == token
    assert received['oauth_redirect_secret'] == "Area 51"
