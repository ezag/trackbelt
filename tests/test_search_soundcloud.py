from urllib.parse import parse_qs, urlparse
import os

import requests
import pytest

from trackbelt import search_soundcloud

real_request = requests.request

def mock_request(raw_url, **kwargs):
    url = urlparse(raw_url)
    method = 'GET'
    assert url.scheme in ('http', 'https')
    assert url.netloc == 'soundcloud.com'
    assert url.params == ''
    assert url.fragment == ''
    path = os.path.join(
        os.path.dirname(__file__), 'responses', url.netloc,
        url.path.strip('/'), url.query, '.'.join((method.lower(), 'html')))
    try:
        with open(path) as f:
            data = f.read()
    except FileNotFoundError:
        data = real_request(method, raw_url, **kwargs).content
        os.makedirs(os.path.dirname(path))
        with open(path, 'w') as f:
            f.write(data.decode('utf-8'))
        pytest.fail(
            'Missing test data for "{} {}" have been written to "{}"'.format(
                method, raw_url, path))
    response = requests.Response()
    response._content = data
    response.status_code = 200
    return response


def test_soundcloud_search_basic(monkeypatch):
    monkeypatch.setattr(requests, 'get', mock_request)
    result = search_soundcloud('evvy', 'collide (keljet remix)')
    assert result == dict(
        title='EVVY - Collide (Keljet Remix)',
        url='/keljet/evvy-collide-keljet-remix-1',
    )


def test_soundcloud_search_empty(monkeypatch):
    monkeypatch.setattr(requests, 'get', mock_request)
    result = search_soundcloud('nonexistentartist', 'nonexistenttitle')
    assert result is None
