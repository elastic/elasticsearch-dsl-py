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


import asyncio
import os
import re
import time
from datetime import datetime
from unittest import SkipTest, TestCase
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.exceptions import ConnectionError
from elasticsearch.helpers import bulk
from pytest import fixture, skip

from elasticsearch_dsl.async_connections import add_connection as add_async_connection
from elasticsearch_dsl.async_connections import connections as async_connections
from elasticsearch_dsl.connections import add_connection, connections

from .test_integration._async import test_document as async_document
from .test_integration._sync import test_document as sync_document
from .test_integration.test_data import (
    DATA,
    FLAT_DATA,
    TEST_GIT_DATA,
    create_flat_git_index,
    create_git_index,
)

if "ELASTICSEARCH_URL" in os.environ:
    ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
else:
    ELASTICSEARCH_URL = "http://localhost:9200"


def get_test_client(wait=True, **kwargs):
    # construct kwargs from the environment
    kw = {"request_timeout": 30}

    if "PYTHON_CONNECTION_CLASS" in os.environ:
        from elasticsearch import connection

        kw["connection_class"] = getattr(
            connection, os.environ["PYTHON_CONNECTION_CLASS"]
        )

    kw.update(kwargs)
    client = Elasticsearch(ELASTICSEARCH_URL, **kw)

    # wait for yellow status
    for tries_left in range(100 if wait else 1, 0, -1):
        try:
            client.cluster.health(wait_for_status="yellow")
            return client
        except ConnectionError:
            if wait and tries_left == 1:
                raise
            time.sleep(0.1)

    raise SkipTest("Elasticsearch failed to start.")


async def get_async_test_client(wait=True, **kwargs):
    # construct kwargs from the environment
    kw = {"request_timeout": 30}

    if "PYTHON_CONNECTION_CLASS" in os.environ:
        from elasticsearch import connection

        kw["connection_class"] = getattr(
            connection, os.environ["PYTHON_CONNECTION_CLASS"]
        )

    kw.update(kwargs)
    client = AsyncElasticsearch(ELASTICSEARCH_URL, **kw)

    # wait for yellow status
    for tries_left in range(100 if wait else 1, 0, -1):
        try:
            await client.cluster.health(wait_for_status="yellow")
            return client
        except ConnectionError:
            if wait and tries_left == 1:
                raise
            await asyncio.sleep(0.1)

    raise SkipTest("Elasticsearch failed to start.")


class ElasticsearchTestCase(TestCase):
    @staticmethod
    def _get_client():
        return get_test_client()

    @classmethod
    def setup_class(cls):
        cls.client = cls._get_client()

    def teardown_method(self, _):
        # Hidden indices expanded in wildcards in ES 7.7
        expand_wildcards = ["open", "closed"]
        if self.es_version() >= (7, 7):
            expand_wildcards.append("hidden")

        self.client.indices.delete_data_stream(
            name="*", ignore=404, expand_wildcards=expand_wildcards
        )
        self.client.indices.delete(
            index="*", ignore=404, expand_wildcards=expand_wildcards
        )
        self.client.indices.delete_template(name="*", ignore=404)

    def es_version(self):
        if not hasattr(self, "_es_version"):
            self._es_version = _get_version(client.info()["version"]["number"])
        return self._es_version


def _get_version(version_string):
    if "." not in version_string:
        return ()
    version = version_string.strip().split(".")
    return tuple(int(v) if v.isdigit() else 999 for v in version)


@fixture(scope="session")
def client():
    try:
        connection = get_test_client(wait="WAIT_FOR_ES" in os.environ)
        add_connection("default", connection)
        return connection
    except SkipTest:
        skip()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    try:
        connection = await get_async_test_client(wait="WAIT_FOR_ES" in os.environ)
        add_async_connection("default", connection)
        return connection
    except SkipTest:
        skip()


@fixture(scope="session")
def es_version(client):
    info = client.info()
    print(info)
    yield tuple(
        int(x)
        for x in re.match(r"^([0-9.]+)", info["version"]["number"]).group(1).split(".")
    )


@fixture
def write_client(client):
    yield client
    for index_name in client.indices.get(index="test-*", expand_wildcards="all"):
        client.indices.delete(index=index_name)
    client.options(ignore_status=404).indices.delete_template(name="test-template")


@pytest_asyncio.fixture
async def async_write_client(async_client):
    yield async_client
    async for index_name in async_client.indices.get(
        index="test-*", expand_wildcards="all"
    ):
        await client.indices.delete(index=index_name)
    await client.options(ignore_status=404).indices.delete_template(
        name="test-template"
    )


@fixture
def mock_client(dummy_response):
    client = Mock()
    client.search.return_value = dummy_response
    add_connection("mock", client)

    yield client
    connections._conn = {}
    connections._kwargs = {}


@fixture
def async_mock_client(dummy_response):
    client = Mock()
    client.search = AsyncMock(return_value=dummy_response)
    client.indices = AsyncMock()
    client.delete_by_query = AsyncMock()
    add_async_connection("mock", client)

    yield client
    async_connections._conn = {}
    async_connections._kwargs = {}


@fixture(scope="session")
def data_client(client):
    # create mappings
    create_git_index(client, "git")
    create_flat_git_index(client, "flat-git")
    # load data
    bulk(client, DATA, raise_on_error=True, refresh=True)
    bulk(client, FLAT_DATA, raise_on_error=True, refresh=True)
    yield client
    client.indices.delete(index="git")
    client.indices.delete(index="flat-git")


@pytest_asyncio.fixture(scope="session")
async def async_data_client(data_client, async_client):
    yield async_client


@fixture
def dummy_response():
    return ObjectApiResponse(
        meta=None,
        body={
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
        },
    )


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
    async_document.PullRequest.init()
    pr = sync_document.PullRequest(
        _id=42,
        comments=[
            sync_document.Comment(
                content="Hello World!",
                author=sync_document.User(name="honzakral"),
                created_at=datetime(2018, 1, 9, 10, 17, 3, 21184),
                history=[
                    sync_document.History(
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


@pytest_asyncio.fixture
async def async_pull_request(async_write_client):
    async_document.PullRequest.init()
    pr = async_document.PullRequest(
        _id=42,
        comments=[
            async_document.Comment(
                content="Hello World!",
                author=async_document.User(name="honzakral"),
                created_at=datetime(2018, 1, 9, 10, 17, 3, 21184),
                history=[
                    async_document.History(
                        timestamp=datetime(2012, 1, 1),
                        diff="-Ahoj Svete!\n+Hello World!",
                    )
                ],
            ),
        ],
        created_at=datetime(2018, 1, 9, 9, 17, 3, 21184),
    )
    await pr.save(refresh=True)
    return pr


@fixture
def setup_ubq_tests(client):
    index = "test-git"
    create_git_index(client, index)
    bulk(client, TEST_GIT_DATA, raise_on_error=True, refresh=True)
    return index


def pytest_collection_modifyitems(items):
    # make sure all async tests are properly marked as such
    pytest_asyncio_tests = (
        item for item in items if pytest_asyncio.is_async_test(item)
    )
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
