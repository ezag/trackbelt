from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen, urlretrieve
import argparse
import codecs
import json
import logging
import os
import sys

import discogs_client
import yaml
from xdg import XDG_CONFIG_HOME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class DownloadAudiosArgs(argparse.ArgumentParser):
    def __init__(self):
        super(DownloadAudiosArgs, self).__init__()
        self.add_argument('command', action='store')
        self.add_argument('uid', action='store')
        self.add_argument('format_string', action='store')


class ListAudiosArgs(argparse.ArgumentParser):
    def __init__(self):
        super(ListAudiosArgs, self).__init__()
        self.add_argument('command', action='store')
        self.add_argument('path', action='store')


class SearchTrackArgs(argparse.ArgumentParser):
    def __init__(self):
        super(SearchTrackArgs, self).__init__()
        self.add_argument('command', action='store')
        self.add_argument('artist', action='store')
        self.add_argument('title', action='store')


class Application(object):
    APP_ID = 4301930
    OAUTH_URL = 'https://oauth.vk.com/authorize'
    AUDIOS_URL = 'https://api.vk.com/method/audio.get'
    REDIRECT_BLANK = 'https://oauth.vk.com/blank.html'


class AuthDisplay(object):
    PAGE = 'page'


class VkPermission(object):
    AUDIO = 8


class ResponseType(object):
    TOKEN = 'token'


def download_audios(uid, format_string):
    auth_url = '{}?{}'.format(
        Application.OAUTH_URL,
        urlencode(dict(
            client_id=Application.APP_ID,
            redirect_uri=Application.REDIRECT_BLANK,
            display=AuthDisplay.PAGE,
            scope=VkPermission.AUDIO,
            response_type=ResponseType.TOKEN,
        ))
    )
    redirect_url = input(
        'Please authenticate at following URL and enter address bar '
        'contents below\n\n{}\n\n> '.format(auth_url))
    access_token = parse_qs(urlparse(redirect_url).fragment)['access_token'][0]
    audios_url = '{}?{}'.format(
        Application.AUDIOS_URL,
        urlencode(dict(
            access_token=access_token,
            owner_id=uid,
        ))
    )
    print(audios_url)
    with urlopen(audios_url) as response:
        audios_info = json.load(codecs.getreader('utf-8')(response))
    audios_count = audios_info['response'][0]
    audios = audios_info['response'][1:]
    print('Count in response is {}, accessible count is {}'.format(
        audios_count, len(audios)))
    for i, audio in enumerate(audios):
        destination = format_string.format(i)
        print('({}/{}) {} - {}\n  <- {}\n  -> {}'.format(
            i, len(audios), audio['artist'], audio['title'], audio['url'],
            destination))
        urlretrieve(audio['url'], destination)


def list_audios(path):
    for filename in os.listdir(path):
        print(filename)


def search_track(artist, title):
    log.info('Searching "%s - %s"', artist, title)
    with open(os.path.join(XDG_CONFIG_HOME, 'vkbelt', 'config.yaml')) as f:
        config = yaml.load(f)
    discogs = discogs_client.Client(
        'vkbelt/1.0', user_token=config['discogs']['user_token'])
    results = discogs.search(artist=artist, track=title)
    for index, result in enumerate(results, 1):
        log.info('Result #%d:\n%s', index, json.dumps(result.data, indent=2))


def main():
    command = sys.argv[1]
    if command == 'download-audios':
        args = DownloadAudiosArgs().parse_args()
        download_audios(args.uid, args.format_string)
    if command == 'list-audios':
        args = ListAudiosArgs().parse_args()
        list_audios(args.path)
    if command == 'search-track':
        args = SearchTrackArgs().parse_args()
        search_track(args.artist, args.title)
    else:
        print('Unknown command "{}"'.format(command))
