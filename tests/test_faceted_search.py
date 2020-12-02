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

from datetime import datetime

from elasticsearch_dsl.faceted_search import (
    DateHistogramFacet,
    FacetedSearch,
    TermsFacet,
)


class BlogSearch(FacetedSearch):
    doc_types = ["user", "post"]
    fields = (
        "title^5",
        "body",
    )

    facets = {
        "category": TermsFacet(field="category.raw"),
        "tags": TermsFacet(field="tags"),
    }


def test_query_is_created_properly():
    bs = BlogSearch("python search")
    s = bs.build_search()

    assert s._doc_type == ["user", "post"]
    assert {
        "aggs": {
            "_filter_tags": {
                "filter": {"match_all": {}},
                "aggs": {"tags": {"terms": {"field": "tags"}}},
            },
            "_filter_category": {
                "filter": {"match_all": {}},
                "aggs": {"category": {"terms": {"field": "category.raw"}}},
            },
        },
        "query": {
            "multi_match": {"fields": ("title^5", "body"), "query": "python search"}
        },
        "highlight": {"fields": {"body": {}, "title": {}}},
    } == s.to_dict()


def test_query_is_created_properly_with_sort_tuple():
    bs = BlogSearch("python search", sort=("category", "-title"))
    s = bs.build_search()

    assert s._doc_type == ["user", "post"]
    assert {
        "aggs": {
            "_filter_tags": {
                "filter": {"match_all": {}},
                "aggs": {"tags": {"terms": {"field": "tags"}}},
            },
            "_filter_category": {
                "filter": {"match_all": {}},
                "aggs": {"category": {"terms": {"field": "category.raw"}}},
            },
        },
        "query": {
            "multi_match": {"fields": ("title^5", "body"), "query": "python search"}
        },
        "highlight": {"fields": {"body": {}, "title": {}}},
        "sort": ["category", {"title": {"order": "desc"}}],
    } == s.to_dict()


def test_filter_is_applied_to_search_but_not_relevant_facet():
    bs = BlogSearch("python search", filters={"category": "elastic"})
    s = bs.build_search()

    assert {
        "aggs": {
            "_filter_tags": {
                "filter": {"terms": {"category.raw": ["elastic"]}},
                "aggs": {"tags": {"terms": {"field": "tags"}}},
            },
            "_filter_category": {
                "filter": {"match_all": {}},
                "aggs": {"category": {"terms": {"field": "category.raw"}}},
            },
        },
        "post_filter": {"terms": {"category.raw": ["elastic"]}},
        "query": {
            "multi_match": {"fields": ("title^5", "body"), "query": "python search"}
        },
        "highlight": {"fields": {"body": {}, "title": {}}},
    } == s.to_dict()


def test_filters_are_applied_to_search_ant_relevant_facets():
    bs = BlogSearch(
        "python search", filters={"category": "elastic", "tags": ["python", "django"]}
    )
    s = bs.build_search()

    d = s.to_dict()

    # we need to test post_filter without relying on order
    f = d["post_filter"]["bool"].pop("must")
    assert len(f) == 2
    assert {"terms": {"category.raw": ["elastic"]}} in f
    assert {"terms": {"tags": ["python", "django"]}} in f

    assert {
        "aggs": {
            "_filter_tags": {
                "filter": {"terms": {"category.raw": ["elastic"]}},
                "aggs": {"tags": {"terms": {"field": "tags"}}},
            },
            "_filter_category": {
                "filter": {"terms": {"tags": ["python", "django"]}},
                "aggs": {"category": {"terms": {"field": "category.raw"}}},
            },
        },
        "query": {
            "multi_match": {"fields": ("title^5", "body"), "query": "python search"}
        },
        "post_filter": {"bool": {}},
        "highlight": {"fields": {"body": {}, "title": {}}},
    } == d


def test_date_histogram_facet_with_1970_01_01_date():
    dhf = DateHistogramFacet()
    assert dhf.get_value({"key": None}) == datetime(1970, 1, 1, 0, 0)
    assert dhf.get_value({"key": 0}) == datetime(1970, 1, 1, 0, 0)
