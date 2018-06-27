from . import alias_migration
from .alias_migration import BlogPost, PATTERN, ALIAS, migrate

def test_alias_migration(write_client):
    # create the index
    alias_migration.setup()

    # verify that template, index, and alias has been set up
    assert write_client.indices.exists_template(name=ALIAS)
    assert write_client.indices.exists(index=PATTERN)
    assert write_client.indices.exists_alias(name=ALIAS)

    indices = write_client.indices.get(index=PATTERN)
    assert len(indices) == 1
    index_name, _ = indices.popitem()

    # which means we can now save a document
    bp = BlogPost(
        _id=0,
        title='Hello World!',
        tags = ['testing', 'dummy'],
        content=open(__file__).read()
    )
    bp.save(refresh=True)

    assert BlogPost.search().count() == 1

    # _matches work which means we get BlogPost instance
    bp = BlogPost.search().execute()[0]
    assert isinstance(bp, BlogPost)
    assert not bp.is_published()
    assert '0' == bp.meta.id

    # create new index
    migrate()

    indices = write_client.indices.get(index=PATTERN)
    assert 2 == len(indices)
    alias = write_client.indices.get(index=ALIAS)
    assert 1 == len(alias)
    assert index_name not in alias

    # data has been moved properly
    assert BlogPost.search().count() == 1

    # _matches work which means we get BlogPost instance
    bp = BlogPost.search().execute()[0]
    assert isinstance(bp, BlogPost)
    assert '0' == bp.meta.id
