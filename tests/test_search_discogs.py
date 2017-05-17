from vkbelt import search_track


def test_discogs_search_basic():
    discogs = None
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
