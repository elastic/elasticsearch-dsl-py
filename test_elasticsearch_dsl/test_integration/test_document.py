from datetime import datetime
from pytz import timezone

from elasticsearch import ConflictError, NotFoundError, RequestError

from elasticsearch_dsl import DocType, Date, Text, Keyword, construct_field, Mapping
from elasticsearch_dsl.utils import AttrList

from pytest import raises

user_field = construct_field('object')
user_field.field('name', 'text', fields={'raw': construct_field('keyword')})

class Wiki(DocType):
    owner = user_field

    class Meta:
        index = 'test-wiki'

class Repository(DocType):
    owner = user_field
    created_at = Date()
    description = Text(analyzer='snowball')
    tags = Keyword()

    @classmethod
    def search(cls):
        return super(Repository, cls).search().filter('term', commit_repo='repo')

    class Meta:
        index = 'git'
        doc_type = 'doc'

class Commit(DocType):
    committed_date = Date()
    authored_date = Date()
    description = Text(analyzer='snowball')

    class Meta:
        index = 'flat-git'
        doc_type = 'doc'
        mapping = Mapping('doc')

def test_update_object_field(write_client):
    Wiki.init()
    w = Wiki(owner={'name': 'Honza Kral'}, _id='elasticsearch-py')
    w.save()

    w.update(owner=[{'name': 'Honza'}, {'name': 'Nick'}])
    assert w.owner[0].name == 'Honza'
    assert w.owner[1].name == 'Nick'

    w = Wiki.get(id='elasticsearch-py')
    assert w.owner[0].name == 'Honza'
    assert w.owner[1].name == 'Nick'

def test_init(write_client):
    Repository.init(index='test-git')

    assert write_client.indices.exists_type(index='test-git', doc_type='doc')

def test_get_raises_404_on_index_missing(data_client):
    with raises(NotFoundError):
        Repository.get('elasticsearch-dsl-php', index='not-there')

def test_get_raises_404_on_non_existent_id(data_client):
    with raises(NotFoundError):
        Repository.get('elasticsearch-dsl-php')

def test_get_returns_none_if_404_ignored(data_client):
    assert None is Repository.get('elasticsearch-dsl-php', ignore=404)

def test_get_returns_none_if_404_ignored_and_index_doesnt_exist(data_client):
    assert None is Repository.get('42', index='not-there', ignore=404)

def test_get(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'
    assert datetime(2014, 3, 3) == elasticsearch_repo.created_at

def test_get_with_tz_date(data_client):
    first_commit = Commit.get(id='3ca6e1e73a071a705b4babd2f581c91a2a3e5037', parent='elasticsearch-dsl-py')

    tzinfo = timezone('Europe/Prague')
    assert tzinfo.localize(datetime(2014, 5, 2, 13, 47, 19, 123000)) == first_commit.authored_date

def test_save_with_tz_date(data_client):
    tzinfo = timezone('Europe/Prague')
    first_commit = Commit.get(id='3ca6e1e73a071a705b4babd2f581c91a2a3e5037', parent='elasticsearch-dsl-py')
    first_commit.committed_date = tzinfo.localize(datetime(2014, 5, 2, 13, 47, 19, 123456))
    first_commit.save()

    first_commit = Commit.get(id='3ca6e1e73a071a705b4babd2f581c91a2a3e5037', parent='elasticsearch-dsl-py')
    assert tzinfo.localize(datetime(2014, 5, 2, 13, 47, 19, 123456)) == first_commit.committed_date

COMMIT_DOCS_WITH_MISSING = [
    {'_id': '0'},                                         # Missing
    {'_id': '3ca6e1e73a071a705b4babd2f581c91a2a3e5037'},  # Existing
    {'_id': 'f'},                                         # Missing
    {'_id': 'eb3e543323f189fd7b698e66295427204fff5755'},  # Existing
]

def test_mget(data_client):
    commits = Commit.mget(COMMIT_DOCS_WITH_MISSING)
    assert commits[0] is None
    assert commits[1]._id == '3ca6e1e73a071a705b4babd2f581c91a2a3e5037'
    assert commits[2] is None
    assert commits[3]._id == 'eb3e543323f189fd7b698e66295427204fff5755'

def test_mget_raises_exception_when_missing_param_is_invalid(data_client):
    with raises(ValueError):
        Commit.mget(COMMIT_DOCS_WITH_MISSING, missing='raj')

def test_mget_raises_404_when_missing_param_is_raise(data_client):
    with raises(NotFoundError):
        Commit.mget(COMMIT_DOCS_WITH_MISSING, missing='raise')

def test_mget_ignores_missing_docs_when_missing_param_is_skip(data_client):
    commits = Commit.mget(COMMIT_DOCS_WITH_MISSING, missing='skip')
    assert commits[0]._id == '3ca6e1e73a071a705b4babd2f581c91a2a3e5037'
    assert commits[1]._id == 'eb3e543323f189fd7b698e66295427204fff5755'

def test_update_works_from_search_response(data_client):
    elasticsearch_repo = Repository.search().execute()[0]

    elasticsearch_repo.update(owner={'other_name': 'elastic'})
    assert 'elastic' == elasticsearch_repo.owner.other_name

    new_version = Repository.get('elasticsearch-dsl-py')
    assert 'elastic' == new_version.owner.other_name
    assert 'elasticsearch' == new_version.owner.name

def test_update(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')
    v = elasticsearch_repo.meta.version

    elasticsearch_repo.update(owner={'new_name': 'elastic'}, new_field='testing-update')

    assert 'elastic' == elasticsearch_repo.owner.new_name
    assert 'testing-update' == elasticsearch_repo.new_field

    # assert version has been updated
    assert elasticsearch_repo.meta.version == v + 1

    new_version = Repository.get('elasticsearch-dsl-py')
    assert 'testing-update' == new_version.new_field
    assert 'elastic' == new_version.owner.new_name
    assert 'elasticsearch' == new_version.owner.name


def test_save_updates_existing_doc(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    elasticsearch_repo.new_field = 'testing-save'
    v = elasticsearch_repo.meta.version
    assert not elasticsearch_repo.save()

    # assert version has been updated
    assert elasticsearch_repo.meta.version == v + 1

    new_repo = data_client.get(index='git', doc_type='doc', id='elasticsearch-dsl-py')
    assert 'testing-save' == new_repo['_source']['new_field']

def test_save_automatically_uses_versions(data_client):
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
        '_type': 'doc',
        '_id': '42',
        '_version': 3,
        '_source': {'description': 'testing'},
    } == write_client.get(index='test-document', doc_type='doc', id=42)

def test_delete(write_client):
    write_client.create(
        index='test-document',
        doc_type='doc',
        id='elasticsearch-dsl-py',
        body={'organization': 'elasticsearch', 'created_at': '2014-03-03', 'owner': {'name': 'elasticsearch'}}
    )

    test_repo = Repository(meta={'id': 'elasticsearch-dsl-py'})
    test_repo.meta.index = 'test-document'
    test_repo.delete()

    assert not write_client.exists(
        index='test-document',
        doc_type='doc',
        id='elasticsearch-dsl-py',
    )

def test_search(data_client):
    assert Repository.search().count() == 1

def test_search_returns_proper_doc_classes(data_client):
    result = Repository.search().execute()

    elasticsearch_repo = result.hits[0]

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'

def test_refresh_mapping(data_client):
    class Commit(DocType):
        class Meta:
            doc_type = 'doc'
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
    assert isinstance(commit.meta.highlight['description'], AttrList)
    assert len(commit.meta.highlight['description']) > 0
