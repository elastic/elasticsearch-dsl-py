# -*- coding: utf-8 -*-
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


import os
from datetime import datetime

from elasticsearch.helpers import bulk
from elasticsearch.helpers.test import SkipTest, get_test_client
from mock import Mock
from pytest import fixture, skip

from elasticsearch_dsl.connections import add_connection, connections

from .test_integration.test_data import (
    DATA,
    FLAT_DATA,
    TEST_GIT_DATA,
    create_flat_git_index,
    create_git_index,
)
from .test_integration.test_document import Comment, History, PullRequest, User


@fixture(scope="session")
def client():
    try:
        connection = get_test_client(nowait="WAIT_FOR_ES" not in os.environ)
        add_connection("default", connection)
        return connection
    except SkipTest:
        skip()


@fixture
def write_client(client):
    yield client
    client.indices.delete("test-*", ignore=404)
    client.indices.delete_template("test-template", ignore=404)


@fixture
def mock_client(dummy_response):
    client = Mock()
    client.search.return_value = dummy_response
    add_connection("mock", client)
    yield client
    connections._conn = {}
    connections._kwargs = {}


@fixture(scope="session")
def data_client(client):
    # create mappings
    create_git_index(client, "git")
    create_flat_git_index(client, "flat-git")
    # load data
    bulk(client, DATA, raise_on_error=True, refresh=True)
    bulk(client, FLAT_DATA, raise_on_error=True, refresh=True)
    yield client
    client.indices.delete("git")
    client.indices.delete("flat-git")


@fixture
def dummy_response():
    return {
        "_shards": {"failed": 0, "successful": 10, "total": 10},
        "hits": {
            "hits": [
                {
                    "_index": "test-index",
                    "_type": "company",
                    "_id": "elasticsearch",
                    "_score": 12.0,
                    "_source": {"city": "Amsterdam", "name": "Elasticsearch"},
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "42",
                    "_score": 11.123,
                    "_routing": "elasticsearch",
                    "_source": {
                        "name": {"first": "Shay", "last": "Bannon"},
                        "lang": "java",
                        "twitter": "kimchy",
                    },
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "47",
                    "_score": 1,
                    "_routing": "elasticsearch",
                    "_source": {
                        "name": {"first": "Honza", "last": "Král"},
                        "lang": "python",
                        "twitter": "honzakral",
                    },
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "53",
                    "_score": 16.0,
                    "_routing": "elasticsearch",
                },
            ],
            "max_score": 12.0,
            "total": 123,
        },
        "timed_out": False,
        "took": 123,
    }


@fixture
def aggs_search():
    from elasticsearch_dsl import Search

    s = Search(index="flat-git")
    s.aggs.bucket("popular_files", "terms", field="files", size=2).metric(
        "line_stats", "stats", field="stats.lines"
    ).metric("top_commits", "top_hits", size=2, _source=["stats.*", "committed_date"])
    s.aggs.bucket(
        "per_month", "date_histogram", interval="month", field="info.committed_date"
    )
    s.aggs.metric("sum_lines", "sum", field="stats.lines")
    return s


@fixture
def aggs_data():
    return {
        "took": 4,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "failed": 0},
        "hits": {"total": 52, "hits": [], "max_score": 0.0},
        "aggregations": {
            "sum_lines": {"value": 25052.0},
            "per_month": {
                "buckets": [
                    {
                        "doc_count": 38,
                        "key": 1393632000000,
                        "key_as_string": "2014-03-01T00:00:00.000Z",
                    },
                    {
                        "doc_count": 11,
                        "key": 1396310400000,
                        "key_as_string": "2014-04-01T00:00:00.000Z",
                    },
                    {
                        "doc_count": 3,
                        "key": 1398902400000,
                        "key_as_string": "2014-05-01T00:00:00.000Z",
                    },
                ]
            },
            "popular_files": {
                "buckets": [
                    {
                        "key": "elasticsearch_dsl",
                        "line_stats": {
                            "count": 40,
                            "max": 228.0,
                            "min": 2.0,
                            "sum": 2151.0,
                            "avg": 53.775,
                        },
                        "doc_count": 40,
                        "top_commits": {
                            "hits": {
                                "total": 40,
                                "hits": [
                                    {
                                        "_id": "3ca6e1e73a071a705b4babd2f581c91a2a3e5037",
                                        "_type": "doc",
                                        "_source": {
                                            "stats": {
                                                "files": 4,
                                                "deletions": 7,
                                                "lines": 30,
                                                "insertions": 23,
                                            },
                                            "committed_date": "2014-05-02T13:47:19",
                                        },
                                        "_score": 1.0,
                                        "_index": "flat-git",
                                    },
                                    {
                                        "_id": "eb3e543323f189fd7b698e66295427204fff5755",
                                        "_type": "doc",
                                        "_source": {
                                            "stats": {
                                                "files": 1,
                                                "deletions": 0,
                                                "lines": 18,
                                                "insertions": 18,
                                            },
                                            "committed_date": "2014-05-01T13:32:14",
                                        },
                                        "_score": 1.0,
                                        "_index": "flat-git",
                                    },
                                ],
                                "max_score": 1.0,
                            }
                        },
                    },
                    {
                        "key": "test_elasticsearch_dsl",
                        "line_stats": {
                            "count": 35,
                            "max": 228.0,
                            "min": 2.0,
                            "sum": 1939.0,
                            "avg": 55.4,
                        },
                        "doc_count": 35,
                        "top_commits": {
                            "hits": {
                                "total": 35,
                                "hits": [
                                    {
                                        "_id": "3ca6e1e73a071a705b4babd2f581c91a2a3e5037",
                                        "_type": "doc",
                                        "_source": {
                                            "stats": {
                                                "files": 4,
                                                "deletions": 7,
                                                "lines": 30,
                                                "insertions": 23,
                                            },
                                            "committed_date": "2014-05-02T13:47:19",
                                        },
                                        "_score": 1.0,
                                        "_index": "flat-git",
                                    },
                                    {
                                        "_id": "dd15b6ba17dd9ba16363a51f85b31f66f1fb1157",
                                        "_type": "doc",
                                        "_source": {
                                            "stats": {
                                                "files": 3,
                                                "deletions": 18,
                                                "lines": 62,
                                                "insertions": 44,
                                            },
                                            "committed_date": "2014-05-01T13:30:44",
                                        },
                                        "_score": 1.0,
                                        "_index": "flat-git",
                                    },
                                ],
                                "max_score": 1.0,
                            }
                        },
                    },
                ],
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 120,
            },
        },
    }


@fixture
def pull_request(write_client):
    PullRequest.init()
    pr = PullRequest(
        _id=42,
        comments=[
            Comment(
                content="Hello World!",
                author=User(name="honzakral"),
                created_at=datetime(2018, 1, 9, 10, 17, 3, 21184),
                history=[
                    History(
                        timestamp=datetime(2012, 1, 1),
                        diff="-Ahoj Svete!\n+Hello World!",
                    )
                ],
            ),
        ],
        created_at=datetime(2018, 1, 9, 9, 17, 3, 21184),
    )
    pr.save(refresh=True)
    return pr


@fixture
def setup_ubq_tests(client):
    index = "test-git"
    create_git_index(client, index)
    bulk(client, TEST_GIT_DATA, raise_on_error=True, refresh=True)
    return index
