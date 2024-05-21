#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.


import pytest
from elasticsearch import ApiError
from pytest import raises

from elasticsearch_dsl import Date, Document, Keyword, MultiSearch, Q, Search, Text
from elasticsearch_dsl.response import aggs

from ..test_data import FLAT_DATA


class Repository(Document):
    created_at = Date()
    description = Text(analyzer="snowball")
    tags = Keyword()

    @classmethod
    def search(cls):
        return super().search().filter("term", commit_repo="repo")

    class Index:
        name = "git"


class Commit(Document):
    class Index:
        name = "flat-git"


@pytest.mark.sync
def test_filters_aggregation_buckets_are_accessible(data_client):
    has_tests_query = Q("term", files="test_elasticsearch_dsl")
    s = Commit.search()[0:0]
    s.aggs.bucket("top_authors", "terms", field="author.name.raw").bucket(
        "has_tests", "filters", filters={"yes": has_tests_query, "no": ~has_tests_query}
    ).metric("lines", "stats", field="stats.lines")

    response = s.execute()

    assert isinstance(
        response.aggregations.top_authors.buckets[0].has_tests.buckets.yes, aggs.Bucket
    )
    assert (
        35
        == response.aggregations.top_authors.buckets[0].has_tests.buckets.yes.doc_count
    )
    assert (
        228
        == response.aggregations.top_authors.buckets[0].has_tests.buckets.yes.lines.max
    )


@pytest.mark.sync
def test_top_hits_are_wrapped_in_response(data_client):
    s = Commit.search()[0:0]
    s.aggs.bucket("top_authors", "terms", field="author.name.raw").metric(
        "top_commits", "top_hits", size=5
    )
    response = s.execute()

    top_commits = response.aggregations.top_authors.buckets[0].top_commits
    assert isinstance(top_commits, aggs.TopHitsData)
    assert 5 == len(top_commits)

    hits = [h for h in top_commits]
    assert 5 == len(hits)
    assert isinstance(hits[0], Commit)


@pytest.mark.sync
def test_inner_hits_are_wrapped_in_response(data_client):
    s = Search(index="git")[0:1].query(
        "has_parent", parent_type="repo", inner_hits={}, query=Q("match_all")
    )
    response = s.execute()

    commit = response.hits[0]
    assert isinstance(commit.meta.inner_hits.repo, response.__class__)
    assert repr(commit.meta.inner_hits.repo[0]).startswith(
        "<Hit(git/elasticsearch-dsl-py): "
    )


@pytest.mark.sync
def test_scan_respects_doc_types(data_client):
    repos = [repo for repo in Repository.search().scan()]

    assert 1 == len(repos)
    assert isinstance(repos[0], Repository)
    assert repos[0].organization == "elasticsearch"


@pytest.mark.sync
def test_scan_iterates_through_all_docs(data_client):
    s = Search(index="flat-git")

    commits = [commit for commit in s.scan()]

    assert 52 == len(commits)
    assert {d["_id"] for d in FLAT_DATA} == {c.meta.id for c in commits}


@pytest.mark.sync
def test_search_after(data_client):
    page_size = 7
    s = Search(index="flat-git")[:page_size].sort("authored_date")
    commits = []
    while True:
        r = s.execute()
        commits += r.hits
        if len(r.hits) < page_size:
            break
        s = r.search_after()

    assert 52 == len(commits)
    assert {d["_id"] for d in FLAT_DATA} == {c.meta.id for c in commits}


@pytest.mark.sync
def test_search_after_no_search(data_client):
    s = Search(index="flat-git")
    with raises(
        ValueError, match="A search must be executed before using search_after"
    ):
        s.search_after()
    s.count()
    with raises(
        ValueError, match="A search must be executed before using search_after"
    ):
        s.search_after()


@pytest.mark.sync
def test_search_after_no_sort(data_client):
    s = Search(index="flat-git")
    r = s.execute()
    with raises(
        ValueError, match="Cannot use search_after when results are not sorted"
    ):
        r.search_after()


@pytest.mark.sync
def test_search_after_no_results(data_client):
    s = Search(index="flat-git")[:100].sort("authored_date")
    r = s.execute()
    assert 52 == len(r.hits)
    s = r.search_after()
    r = s.execute()
    assert 0 == len(r.hits)
    with raises(
        ValueError, match="Cannot use search_after when there are no search results"
    ):
        r.search_after()


@pytest.mark.sync
def test_response_is_cached(data_client):
    s = Repository.search()
    repos = [repo for repo in s]

    assert hasattr(s, "_response")
    assert s._response.hits == repos


@pytest.mark.sync
def test_multi_search(data_client):
    s1 = Repository.search()
    s2 = Search(index="flat-git")

    ms = MultiSearch()
    ms = ms.add(s1).add(s2)

    r1, r2 = ms.execute()

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1._search is s1

    assert 52 == r2.hits.total.value
    assert r2._search is s2


@pytest.mark.sync
def test_multi_missing(data_client):
    s1 = Repository.search()
    s2 = Search(index="flat-git")
    s3 = Search(index="does_not_exist")

    ms = MultiSearch()
    ms = ms.add(s1).add(s2).add(s3)

    with raises(ApiError):
        ms.execute()

    r1, r2, r3 = ms.execute(raise_on_error=False)

    assert 1 == len(r1)
    assert isinstance(r1[0], Repository)
    assert r1._search is s1

    assert 52 == r2.hits.total.value
    assert r2._search is s2

    assert r3 is None


@pytest.mark.sync
def test_raw_subfield_can_be_used_in_aggs(data_client):
    s = Search(index="git")[0:0]
    s.aggs.bucket("authors", "terms", field="author.name.raw", size=1)

    r = s.execute()

    authors = r.aggregations.authors
    assert 1 == len(authors)
    assert {"key": "Honza Král", "doc_count": 52} == authors[0]
