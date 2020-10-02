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

from copy import deepcopy

from elasticsearch_dsl import Q, UpdateByQuery


def test_ubq_starts_with_no_query():
    ubq = UpdateByQuery()

    assert ubq.query._proxied is None


def test_ubq_to_dict():
    ubq = UpdateByQuery()
    assert {} == ubq.to_dict()

    ubq = ubq.query("match", f=42)
    assert {"query": {"match": {"f": 42}}} == ubq.to_dict()

    assert {"query": {"match": {"f": 42}}, "size": 10} == ubq.to_dict(size=10)

    ubq = UpdateByQuery(extra={"size": 5})
    assert {"size": 5} == ubq.to_dict()


def test_complex_example():
    ubq = UpdateByQuery()
    ubq = (
        ubq.query("match", title="python")
        .query(~Q("match", title="ruby"))
        .filter(Q("term", category="meetup") | Q("term", category="conference"))
        .script(
            source="ctx._source.likes += params.f", lang="painless", params={"f": 3}
        )
    )

    ubq.query.minimum_should_match = 2
    assert {
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {"term": {"category": "meetup"}},
                                {"term": {"category": "conference"}},
                            ]
                        }
                    }
                ],
                "must": [{"match": {"title": "python"}}],
                "must_not": [{"match": {"title": "ruby"}}],
                "minimum_should_match": 2,
            }
        },
        "script": {
            "source": "ctx._source.likes += params.f",
            "lang": "painless",
            "params": {"f": 3},
        },
    } == ubq.to_dict()


def test_exclude():
    ubq = UpdateByQuery()
    ubq = ubq.exclude("match", title="python")

    assert {
        "query": {
            "bool": {
                "filter": [{"bool": {"must_not": [{"match": {"title": "python"}}]}}]
            }
        }
    } == ubq.to_dict()


def test_reverse():
    d = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "should": [
                            {"term": {"category": "meetup"}},
                            {"term": {"category": "conference"}},
                        ]
                    }
                },
                "query": {
                    "bool": {
                        "must": [{"match": {"title": "python"}}],
                        "must_not": [{"match": {"title": "ruby"}}],
                        "minimum_should_match": 2,
                    }
                },
            }
        },
        "script": {
            "source": "ctx._source.likes += params.f",
            "lang": "painless",
            "params": {"f": 3},
        },
    }

    d2 = deepcopy(d)

    ubq = UpdateByQuery.from_dict(d)

    assert d == d2
    assert d == ubq.to_dict()


def test_from_dict_doesnt_need_query():
    ubq = UpdateByQuery.from_dict({"script": {"source": "test"}})

    assert {"script": {"source": "test"}} == ubq.to_dict()


def test_params_being_passed_to_search(mock_client):
    ubq = UpdateByQuery(using="mock")
    ubq = ubq.params(routing="42")
    ubq.execute()

    mock_client.update_by_query.assert_called_once_with(
        index=None, body={}, routing="42"
    )


def test_overwrite_script():
    ubq = UpdateByQuery()
    ubq = ubq.script(
        source="ctx._source.likes += params.f", lang="painless", params={"f": 3}
    )
    assert {
        "script": {
            "source": "ctx._source.likes += params.f",
            "lang": "painless",
            "params": {"f": 3},
        }
    } == ubq.to_dict()
    ubq = ubq.script(source="ctx._source.likes++")
    assert {"script": {"source": "ctx._source.likes++"}} == ubq.to_dict()
