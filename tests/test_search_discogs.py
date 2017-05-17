from urllib.parse import parse_qs, urlparse
import yaml
import json
import os.path

from xdg import XDG_CONFIG_HOME
import discogs_client
import requests
import pytest

from vkbelt import search_track


real_request = requests.request
with open(os.path.join(os.path.dirname(__file__), 'responses.json')) as f:
    RESPONSES = json.load(f)


def mock_request(method, raw_url, **kwargs):
    url = urlparse(raw_url)
    assert method == 'GET'
    assert url.scheme in ('http', 'https')
    assert url.netloc == 'api.discogs.com'
    assert url.params == ''
    assert url.fragment == ''
    response = requests.Response()
    try:
        response._content = json.dumps(
            RESPONSES[url.path][url.query]).encode('utf-8')
        response.status_code = 200
    except KeyError:
        with open(os.path.join(XDG_CONFIG_HOME, 'vkbelt', 'config.yaml')) as f:
            config = yaml.load(f)
        kwargs['params']['token'] = config['discogs']['user_token']
        response = real_request(method, raw_url, **kwargs)
        json_response = json.dumps({url.path: {url.query: response.json()}},
                                   sort_keys=True, indent=2)
        with open('test-real-response.json', 'w') as f:
            f.write(json_response)
        pytest.fail('Missing test data for {}\n\n{}'.format(
            raw_url, json_response))
    else:
        return response


def test_discogs_search_basic(monkeypatch):
    monkeypatch.setattr(requests, 'request', mock_request)
    discogs = discogs_client.Client('vkbelt', user_token='qwe')
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
