from urllib.parse import urlencode, urlunparse
import json
import logging
import os.path

from bs4 import BeautifulSoup
from xdg import XDG_CONFIG_HOME
import click
import discogs_client
import requests
import yaml


def read_config():
    with open(os.path.join(XDG_CONFIG_HOME, 'vkbelt', 'config.yaml')) as f:
        return yaml.load(f)


def discogs_client_from_config(trackbelt_config):
    return discogs_client.Client(
        'trackbelt/1.0', user_token=trackbelt_config['discogs']['user_token'])


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
config = read_config()
discogs = discogs_client_from_config(config)


def decompose_query(query):
    artist, title = query.split(' - ')
    return dict(
        artist=artist,
        title=title,
    )


def search_track(query):
    kwargs = decompose_query(query)
    log.info('Decomposed query: %s', json.dumps(kwargs, indent=2))
    discogs_result = search_discogs(**kwargs)
    soundcloud_result = search_soundcloud(**kwargs)
    return dict(
        query=query,
        discogs=discogs_result,
        soundcloud=soundcloud_result,
    )


def search_discogs(artist, title):

    def is_main_release_or_has_no_master(release):
        if release.master is not None:
            log.debug('Release %d has master %d...', release.id, release.master.id)
            if release == release.master.main_release:
                log.debug('...and is the main release!')
            else:
                log.debug('...but is not the main (main is %d)', release.master.main_release.id)
                return False
        else:
            log.debug('Release %d has no master', release.id)
        return True

    def track_name_does_match(actual, looking_for):
        if actual.lower() == looking_for.lower():
            log.debug('Track name "%s" is exact match', actual)
            return True
        return False

    results = discogs.search(type='release', artist=artist, track=title)
    log.debug('Got %d search results', len(results))
    for result in results:
        log.debug('Release %d: %s', result.id, result.title)
        if not is_main_release_or_has_no_master(result):
            log.debug('Skipping release %d because it is not the main', result.id)
            continue
        matching_artists = [a for a in result.artists
                            if a.name.lower() == artist.lower()]
        if not matching_artists:
            continue
        assert len(matching_artists) == 1
        matching_artist = matching_artists[0]
        log.debug('Artist %d does match: %s', matching_artist.id, matching_artist.name)
        for track in result.tracklist:
            if not track_name_does_match(track.title, title):
                log.debug('Track name mismatch: %s', track.title)
                continue
            return dict(
                artist=matching_artist.name,
                title=track.title,
                duration=track.duration,
                release_id=result.id,
                master_id=result.master.id if result.master is not None else None,
                track_position=track.position,
            )
        log.debug('Skipping release %d because none of tracks matched', result.id)


def search_soundcloud(artist, title):
    try:
        results = [(row.a.get_text(), row.a['href']) for row in
                   BeautifulSoup(requests.get(urlunparse((
                       'https', 'soundcloud.com', 'search', None,
                       urlencode(dict(q='{} - {}'.format(artist, title))), None,
                   ))).content, 'html.parser').find_all('ul')[1].find_all('li')]
    except IndexError:
        return None
    title, url = results[0]
    return dict(
        title=title,
        url=url,
    )


@click.command()
@click.option('-q')
@click.option('-f',)
def cmd_search_track(q, f):
    if q is not None and f is not None:
        log.error('Either q of f please')
        return
    if q is not None:
        log.info('Searching "%s"', q)
        result = search_track(q)
        log.info('Result: %s', json.dumps(result, indent=2))
    if f is not None:
        log.info('Reading inputs from "%s"', f)
        # TODO: read playlist from file
