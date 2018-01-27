from trackbelt import decompose_query


def test_basic_query():
    query = decompose_query('tricky - forget')
    assert query['artist'] == 'tricky'
    assert query['title'] == 'forget'

def test_remix_query():
    query = decompose_query('Evvy - Collide (Keljet Remix)')
    assert query['artist'] == 'Evvy'
    assert query['title'] == 'Collide (Keljet Remix)'
