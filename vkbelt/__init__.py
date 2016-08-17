from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen, urlretrieve
import argparse
import codecs
import json


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__()
        self.add_argument('command', action='store')
        self.add_argument('uid', action='store')
        self.add_argument('format_string', action='store')


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


def main():
    args = ArgumentParser().parse_args()
    if args.command == 'download-audios':
        download_audios(args.uid, args.format_string)
    else:
        print('Unknown command "{}"'.format(args.command))
