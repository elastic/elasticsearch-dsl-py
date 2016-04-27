from elasticsearch import TransportError

from elasticsearch_dsl import Search, DocType, Date, String, MultiSearch, \
    MetaField, Index, Q

from .test_data import DATA

from pytest import raises

class Repository(DocType):
    created_at = Date()
    description = String(analyzer='snowball')
    tags = String(index='not_analyzed')

    class Meta:
        index = 'git'
        doc_type = 'repos'

class Commit(DocType):
    class Meta:
        doc_type = 'commits'
        index = 'git'
        parent = MetaField(type='repos')

def test_inner_hits_are_wrapped_in_response(data_client):
    i = Index('git')
    i.doc_type(Repository)
    i.doc_type(Commit)
    s = i.search()[0:1].doc_type(Commit).query('has_parent', type='repos', inner_hits={}, query=Q('match_all'))
    response = s.execute()

    commit = response.hits[0]
    assert isinstance(commit.meta.inner_hits.repos, response.__class__)
    assert isinstance(commit.meta.inner_hits.repos[0], Repository)

def test_suggest_can_be_run_separately(data_client):
    s = Search()
    s = s.suggest('simple_suggestion', 'elasticserach', term={'field': 'organization'})
    response = s.execute_suggest()

    assert response.success()
    assert response.simple_suggestion[0].options[0].text == 'elasticsearch'

def test_scan_respects_doc_types(data_client):
    repos = list(Repository.search().scan())

    assert 1 == len(repos)
    assert isinstance(repos[0], Repository)

def test_scan_iterates_through_all_docs(data_client):
    s = Search(index='git').filter('term', _type='commits')

    commits = list(s.scan())

    assert 52 == len(commits)
    assert set(d['_id'] for d in DATA if d['_type'] == 'commits') == set(c.meta.id for c in commits)

def test_response_is_cached(data_client):
    s = Repository.search()
    repos = list(s)

    assert hasattr(s, '_response')
    assert s._response.hits == repos

def test_multi_search(data_client):
    s1 = Repository.search()
    s2 = Search(doc_type='commits')

    ms = MultiSearch(index='git')
    ms = ms.add(s1).add(s2)

    r1, r2 = ms.execute()

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1.search is s1

    assert 52 == r2.hits.total
    assert r2.search is s2

def test_multi_missing(data_client):
    s1 = Repository.search()
    s2 = Search(doc_type='commits')
    s3 = Search(index='does_not_exist')

    ms = MultiSearch()
    ms = ms.add(s1).add(s2).add(s3)

    with raises(TransportError):
        ms.execute()

    r1, r2, r3 = ms.execute(raise_on_error=False)

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1.search is s1

    assert 52 == r2.hits.total
    assert r2.search is s2

    assert r3 is None
