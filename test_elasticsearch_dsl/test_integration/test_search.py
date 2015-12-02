from elasticsearch_dsl import Search, DocType, Date, String, MultiSearch

from .test_data import DATA

class Repository(DocType):
    created_at = Date()
    description = String(analyzer='snowball')
    tags = String(index='not_analyzed')

    class Meta:
        index = 'git'
        doc_type = 'repos'

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
