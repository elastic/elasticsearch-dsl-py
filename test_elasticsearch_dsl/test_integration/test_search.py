# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from elasticsearch import TransportError

from elasticsearch_dsl import Search, DocType, Date, Text, Keyword, MultiSearch, \
    Index, Q
from elasticsearch_dsl.response import aggs

from .test_data import FLAT_DATA

from pytest import raises

class Repository(DocType):
    created_at = Date()
    description = Text(analyzer='snowball')
    tags = Keyword()

    @classmethod
    def search(cls):
        return super(Repository, cls).search().filter('term', commit_repo='repo')

    class Meta:
        index = 'git'

class Commit(DocType):
    class Meta:
        index = 'flat-git'

def test_filters_aggregation_buckets_are_accessible(data_client):
    has_tests_query = Q('term', files='test_elasticsearch_dsl')
    s = Commit.search()[0:0]
    s.aggs\
        .bucket('top_authors', 'terms', field='author.name.raw')\
        .bucket('has_tests', 'filters', filters={'yes': has_tests_query, 'no': ~has_tests_query})\
        .metric('lines', 'stats', field='stats.lines')
    response = s.execute()

    assert isinstance(response.aggregations.top_authors.buckets[0].has_tests.buckets.yes, aggs.Bucket)
    assert 35 == response.aggregations.top_authors.buckets[0].has_tests.buckets.yes.doc_count
    assert 228 == response.aggregations.top_authors.buckets[0].has_tests.buckets.yes.lines.max

def test_top_hits_are_wrapped_in_response(data_client):
    s = Commit.search()[0:0]
    s.aggs.bucket('top_authors', 'terms', field='author.name.raw').metric('top_commits', 'top_hits', size=5)
    response = s.execute()

    top_commits = response.aggregations.top_authors.buckets[0].top_commits
    assert isinstance(top_commits, aggs.TopHitsData)
    assert 5 == len(top_commits)

    hits = [h for h in top_commits]
    assert 5 == len(hits)
    assert isinstance(hits[0], Commit)


def test_inner_hits_are_wrapped_in_response(data_client):
    s = Search(index='git')[0:1].query('has_parent', parent_type='repo', inner_hits={}, query=Q('match_all'))
    response = s.execute()

    commit = response.hits[0]
    assert isinstance(commit.meta.inner_hits.repo, response.__class__)
    assert repr(commit.meta.inner_hits.repo[0]).startswith("<Hit(git/doc/elasticsearch-dsl-py): ")

def test_scan_respects_doc_types(data_client):
    repos = list(Repository.search().scan())

    assert 1 == len(repos)
    assert isinstance(repos[0], Repository)
    assert repos[0].organization == 'elasticsearch'

def test_scan_iterates_through_all_docs(data_client):
    s = Search(index='flat-git')

    commits = list(s.scan())

    assert 52 == len(commits)
    assert set(d['_id'] for d in FLAT_DATA) == set(c.meta.id for c in commits)

def test_response_is_cached(data_client):
    s = Repository.search()
    repos = list(s)

    assert hasattr(s, '_response')
    assert s._response.hits == repos

def test_multi_search(data_client):
    s1 = Repository.search()
    s2 = Search(index='flat-git')

    ms = MultiSearch()
    ms = ms.add(s1).add(s2)

    r1, r2 = ms.execute()

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1._search is s1

    assert 52 == r2.hits.total
    assert r2._search is s2

def test_multi_missing(data_client):
    s1 = Repository.search()
    s2 = Search(index='flat-git')
    s3 = Search(index='does_not_exist')

    ms = MultiSearch()
    ms = ms.add(s1).add(s2).add(s3)

    with raises(TransportError):
        ms.execute()

    r1, r2, r3 = ms.execute(raise_on_error=False)

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1._search is s1

    assert 52 == r2.hits.total
    assert r2._search is s2

    assert r3 is None

def test_raw_subfield_can_be_used_in_aggs(data_client):
    s = Search(index='git')[0:0]
    s.aggs.bucket('authors', 'terms', field='author.name.raw', size=1)

    r = s.execute()

    authors = r.aggregations.authors
    assert 1 == len(authors)
    assert {'key': 'Honza Král', 'doc_count': 52} == authors[0]
