from .percolate import setup, BlogPost

def test_post_gets_tagged_automatically(write_client):
    setup()

    bp = BlogPost(_id=47, content='nothing about snakes here!')
    bp_py = BlogPost(_id=42, content='something about Python here!')

    bp.save()
    bp_py.save()

    assert [] == bp.tags
    assert set(('programming', 'development', 'python')) == set(bp_py.tags)
