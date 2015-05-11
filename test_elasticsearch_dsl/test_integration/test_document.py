from datetime import datetime
from pytz import timezone

from elasticsearch import ConflictError, NotFoundError

from elasticsearch_dsl import DocType, Date, String, construct_field, Mapping

from pytest import raises

user_field = construct_field('object')
user_field.field('name', 'string', fields={'raw': construct_field('string', index='not_analyzed')})

class Repository(DocType):
    owner = user_field
    created_at = Date()
    description = String(analyzer='snowball')
    tags = String(index='not_analyzed')

    class Meta:
        index = 'git'
        doc_type = 'repos'

class Commit(DocType):
    committed_date = Date()
    authored_date = Date()
    description = String(analyzer='snowball')

    class Meta:
        index = 'git'
        mapping = Mapping('commits')
        mapping.meta('_parent', type='repos')

def test_parent_type_is_exposed():
    assert Commit._doc_type.parent == 'repos'
    assert Repository._doc_type.parent is None

def test_init(write_client):
    Repository.init(index='test-git')

    assert write_client.indices.exists_type(index='test-git', doc_type='repos')

def test_get_raises_404_on_non_existent_id(data_client):
    with raises(NotFoundError):
        Repository.get('elasticsearch-dsl-php')

def test_get(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'
    assert datetime(2014, 3, 3) == elasticsearch_repo.created_at

def test_get_with_tz_date(data_client):
    first_commit = Commit.get(id='3ca6e1e73a071a705b4babd2f581c91a2a3e5037', parent='elasticsearch-dsl-py')

    tzinfo = timezone('Europe/Prague')
    assert tzinfo.localize(datetime(2014, 5, 2, 13, 47, 19)) == first_commit.authored_date

def test_save_updates_existing_doc(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    elasticsearch_repo.new_field = 'testing'
    v = elasticsearch_repo.meta.version
    assert not elasticsearch_repo.save()

    # assert version has been updated
    assert elasticsearch_repo.meta.version == v + 1

    new_repo = data_client.get(index='git', doc_type='repos', id='elasticsearch-dsl-py')
    assert 'testing' == new_repo['_source']['new_field']

def test_save_automatially_uses_versions(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')
    elasticsearch_repo.meta.version += 1

    with raises(ConflictError):
        elasticsearch_repo.save()

def test_can_save_to_different_index(write_client):
    test_repo = Repository(description='testing', meta={'id': 42})
    test_repo.meta.version_type = 'external'
    test_repo.meta.version = 3
    assert test_repo.save(index='test-document')

    assert {
        'found': True,
        '_index': 'test-document',
        '_type': 'repos',
        '_id': '42',
        '_version': 3,
        '_source': {'description': 'testing'},
    } == write_client.get(index='test-document', doc_type='repos', id=42)

def test_delete(write_client):
    write_client.create(
        index='test-document',
        doc_type='repos',
        id='elasticsearch-dsl-py',
        body={'organization': 'elasticsearch', 'created_at': '2014-03-03', 'owner': {'name': 'elasticsearch'}}
    )

    test_repo = Repository(meta={'id': 'elasticsearch-dsl-py'})
    test_repo.meta.index = 'test-document'
    test_repo.delete()

    assert not write_client.exists(
        index='test-document',
        doc_type='repos',
        id='elasticsearch-dsl-py',
    )

def test_search(data_client):
    assert Repository.search().count() == 1

def test_search_returns_proper_doc_classes(data_client):
    result = Repository.search().execute()

    elasticsearch_repo = result.hits[0]

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'

def test_search_with_fields(data_client):
    s = Commit.search()
    s = s.filter('term', _id='3ca6e1e73a071a705b4babd2f581c91a2a3e5037')
    s = s.fields(['_parent', 'parent_shas'])
    results = s.execute()

    commit = results.hits[0]
    assert 'elasticsearch-dsl-py' == commit.meta.parent
    assert ['eb3e543323f189fd7b698e66295427204fff5755'] == commit.parent_shas


def test_refresh_mapping(data_client):
    class Commit(DocType):
        class Meta:
            doc_type = 'commits'
            index = 'git'

    Commit._doc_type.refresh()

    assert 'stats' in Commit._doc_type.mapping
    assert 'committer' in Commit._doc_type.mapping
    assert 'description' in Commit._doc_type.mapping
    assert 'committed_date' in Commit._doc_type.mapping
    assert isinstance(Commit._doc_type.mapping['committed_date'], Date)

def test_highlight_in_meta(data_client):
    commit = Commit.search().query('match', description='inverting').highlight('description').execute()[0]

    assert isinstance(commit, Commit)
    assert 'description' in commit.meta.highlight
    assert isinstance(commit.meta.highlight['description'], list)
    assert len(commit.meta.highlight['description']) > 0
