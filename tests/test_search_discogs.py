from urllib.parse import parse_qs, urlparse
import yaml
import json
import os

from xdg import XDG_CONFIG_HOME
import discogs_client
import requests
import pytest

from trackbelt import search_track

real_request = requests.request

def mock_request(method, raw_url, **kwargs):
    url = urlparse(raw_url)
    assert method == 'GET'
    assert url.scheme in ('http', 'https')
    assert url.netloc == 'api.discogs.com'
    assert url.params == ''
    assert url.fragment == ''
    path = os.path.join(
        os.path.dirname(__file__), 'responses', url.netloc,
        url.path.strip('/'), url.query, '.'.join((method.lower(), 'json')))
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        with open(os.path.join(XDG_CONFIG_HOME, 'vkbelt', 'config.yaml')) as f:
            config = yaml.load(f)
        if 'params' not in kwargs:
            kwargs['params'] = {}
        kwargs['params']['token'] = config['discogs']['user_token']
        data = real_request(method, raw_url, **kwargs).json()
        os.makedirs(os.path.dirname(path))
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        pytest.fail(
            'Missing test data for "{} {}" have been written to "{}"'.format(
                method, raw_url, path))
    response = requests.Response()
    response._content = json.dumps(data).encode('utf-8')
    response.status_code = 200
    return response


def test_discogs_search_basic(monkeypatch):
    monkeypatch.setattr(requests, 'request', mock_request)
    discogs = discogs_client.Client('vkbelt')
    result = search_track(discogs, 'tricky', 'forget')
    assert result == dict(
        artist='Tricky',
        title='Forget',
        duration='3:46',
        discogs=dict(
            release_id=5914226,
            track_position=3,
        )
    )
