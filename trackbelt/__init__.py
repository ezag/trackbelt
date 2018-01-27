import json
import logging
import os.path

from xdg import XDG_CONFIG_HOME
import click
import discogs_client
import yaml

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def decompose_query(query):
    artist, title = query.split(' - ')
    return dict(
        artist=artist,
        title=title,
    )


def search_track(discogs, query):
    kwargs = decompose_query(query)
    log.info('Decomposed query: %s', json.dumps(kwargs, indent=2))
    discogs_result = search_discogs(discogs, **kwargs)
    return dict(
        query=query,
        discogs=discogs_result,
    )


def search_discogs(discogs, artist, title):
    results = discogs.search(type='release', artist=artist, track=title)
    for result in results:
        matching_artists = [a for a in result.artists
                            if a.name.lower() == artist.lower()]
        if not matching_artists:
            continue
        assert len(matching_artists) == 1
        matching_artist = matching_artists[0]
        for track in result.tracklist:
            if track.title.lower() != title.lower():
                continue
            return dict(
                artist=matching_artist.name,
                title=track.title,
                duration=track.duration,
                discogs=dict(
                    release_id=result.id,
                    track_position=int(track.position),
                )
            )


@click.command()
@click.argument('query')
def cmd_search_track(query):
    log.info('Searching "%s"', query)
    with open(os.path.join(XDG_CONFIG_HOME, 'vkbelt', 'config.yaml')) as f:
        config = yaml.load(f)
    discogs = discogs_client.Client(
        'trackbelt/1.0', user_token=config['discogs']['user_token'])
    result = search_track(discogs, query)
    log.info('Result: %s', json.dumps(result, indent=2))
