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

from pytest import raises

from elasticsearch_dsl import function, query


def test_empty_Q_is_match_all():
    q = query.Q()

    assert isinstance(q, query.MatchAll)
    assert query.MatchAll() == q


def test_match_to_dict():
    assert {"match": {"f": "value"}} == query.Match(f="value").to_dict()


def test_match_to_dict_extra():
    assert {"match": {"f": "value", "boost": 2}} == query.Match(
        f="value", boost=2
    ).to_dict()


def test_fuzzy_to_dict():
    assert {"fuzzy": {"f": "value"}} == query.Fuzzy(f="value").to_dict()


def test_prefix_to_dict():
    assert {"prefix": {"f": "value"}} == query.Prefix(f="value").to_dict()


def test_term_to_dict():
    assert {"term": {"_type": "article"}} == query.Term(_type="article").to_dict()


def test_bool_to_dict():
    bool = query.Bool(must=[query.Match(f="value")], should=[])

    assert {"bool": {"must": [{"match": {"f": "value"}}]}} == bool.to_dict()


def test_dismax_to_dict():
    assert {"dis_max": {"queries": [{"term": {"_type": "article"}}]}} == query.DisMax(
        queries=[query.Term(_type="article")]
    ).to_dict()


def test_bool_from_dict_issue_318():
    d = {"bool": {"must_not": {"match": {"field": "value"}}}}
    q = query.Q(d)

    assert q == ~query.Match(field="value")


def test_repr():
    bool = query.Bool(must=[query.Match(f="value")], should=[])

    assert "Bool(must=[Match(f='value')])" == repr(bool)


def test_query_clone():
    bool = query.Bool(
        must=[query.Match(x=42)],
        should=[query.Match(g="v2")],
        must_not=[query.Match(title="value")],
    )
    bool_clone = bool._clone()

    assert bool == bool_clone
    assert bool is not bool_clone


def test_bool_converts_its_init_args_to_queries():
    q = query.Bool(must=[{"match": {"f": "value"}}])

    assert len(q.must) == 1
    assert q.must[0] == query.Match(f="value")


def test_two_queries_make_a_bool():
    q1 = query.Match(f="value1")
    q2 = query.Match(message={"query": "this is a test", "opeartor": "and"})
    q = q1 & q2

    assert isinstance(q, query.Bool)
    assert [q1, q2] == q.must


def test_other_and_bool_appends_other_to_must():
    q1 = query.Match(f="value1")
    qb = query.Bool()

    q = q1 & qb
    assert q is not qb
    assert q.must[0] == q1


def test_bool_and_other_appends_other_to_must():
    q1 = query.Match(f="value1")
    qb = query.Bool()

    q = qb & q1
    assert q is not qb
    assert q.must[0] == q1


def test_bool_and_other_sets_min_should_match_if_needed():
    q1 = query.Q("term", category=1)
    q2 = query.Q(
        "bool", should=[query.Q("term", name="aaa"), query.Q("term", name="bbb")]
    )

    q = q1 & q2
    assert q == query.Bool(
        must=[q1],
        should=[query.Q("term", name="aaa"), query.Q("term", name="bbb")],
        minimum_should_match=1,
    )


def test_bool_with_different_minimum_should_match_should_not_be_combined():
    q1 = query.Q(
        "bool",
        minimum_should_match=2,
        should=[
            query.Q("term", field="aa1"),
            query.Q("term", field="aa2"),
            query.Q("term", field="aa3"),
            query.Q("term", field="aa4"),
        ],
    )
    q2 = query.Q(
        "bool",
        minimum_should_match=3,
        should=[
            query.Q("term", field="bb1"),
            query.Q("term", field="bb2"),
            query.Q("term", field="bb3"),
            query.Q("term", field="bb4"),
        ],
    )
    q3 = query.Q(
        "bool",
        minimum_should_match=4,
        should=[
            query.Q("term", field="cc1"),
            query.Q("term", field="cc2"),
            query.Q("term", field="cc3"),
            query.Q("term", field="cc4"),
        ],
    )

    q4 = q1 | q2
    assert q4 == query.Bool(should=[q1, q2])

    q5 = q1 | q2 | q3
    assert q5 == query.Bool(should=[q1, q2, q3])


def test_empty_bool_has_min_should_match_0():
    assert 0 == query.Bool()._min_should_match


def test_query_and_query_creates_bool():
    q1 = query.Match(f=42)
    q2 = query.Match(g=47)

    q = q1 & q2
    assert isinstance(q, query.Bool)
    assert q.must == [q1, q2]


def test_match_all_and_query_equals_other():
    q1 = query.Match(f=42)
    q2 = query.MatchAll()

    q = q1 & q2
    assert q1 == q


def test_not_match_all_is_match_none():
    q = query.MatchAll()

    assert ~q == query.MatchNone()


def test_not_match_none_is_match_all():
    q = query.MatchNone()

    assert ~q == query.MatchAll()


def test_match_none_or_query_equals_query():
    q1 = query.Match(f=42)
    q2 = query.MatchNone()

    assert q1 | q2 == query.Match(f=42)


def test_match_none_and_query_equals_match_none():
    q1 = query.Match(f=42)
    q2 = query.MatchNone()

    assert q1 & q2 == query.MatchNone()


def test_bool_and_bool():
    qt1, qt2, qt3 = query.Match(f=1), query.Match(f=2), query.Match(f=3)

    q1 = query.Bool(must=[qt1], should=[qt2])
    q2 = query.Bool(must_not=[qt3])
    assert q1 & q2 == query.Bool(
        must=[qt1], must_not=[qt3], should=[qt2], minimum_should_match=0
    )

    q1 = query.Bool(must=[qt1], should=[qt1, qt2])
    q2 = query.Bool(should=[qt3])
    assert q1 & q2 == query.Bool(
        must=[qt1, qt3], should=[qt1, qt2], minimum_should_match=0
    )


def test_bool_and_bool_with_min_should_match():
    qt1, qt2 = query.Match(f=1), query.Match(f=2)
    q1 = query.Q("bool", minimum_should_match=1, should=[qt1])
    q2 = query.Q("bool", minimum_should_match=1, should=[qt2])

    assert query.Q("bool", must=[qt1, qt2]) == q1 & q2


def test_inverted_query_becomes_bool_with_must_not():
    q = query.Match(f=42)

    assert ~q == query.Bool(must_not=[query.Match(f=42)])


def test_inverted_query_with_must_not_become_should():
    q = query.Q("bool", must_not=[query.Q("match", f=1), query.Q("match", f=2)])

    assert ~q == query.Q("bool", should=[query.Q("match", f=1), query.Q("match", f=2)])


def test_inverted_query_with_must_and_must_not():
    q = query.Q(
        "bool",
        must=[query.Q("match", f=3), query.Q("match", f=4)],
        must_not=[query.Q("match", f=1), query.Q("match", f=2)],
    )
    print((~q).to_dict())
    assert ~q == query.Q(
        "bool",
        should=[
            # negation of must
            query.Q("bool", must_not=[query.Q("match", f=3)]),
            query.Q("bool", must_not=[query.Q("match", f=4)]),
            # negation of must_not
            query.Q("match", f=1),
            query.Q("match", f=2),
        ],
    )


def test_double_invert_returns_original_query():
    q = query.Match(f=42)

    assert q == ~~q


def test_bool_query_gets_inverted_internally():
    q = query.Bool(must_not=[query.Match(f=42)], must=[query.Match(g="v")])

    assert ~q == query.Bool(
        should=[
            # negating must
            query.Bool(must_not=[query.Match(g="v")]),
            # negating must_not
            query.Match(f=42),
        ]
    )


def test_match_all_or_something_is_match_all():
    q1 = query.MatchAll()
    q2 = query.Match(f=42)

    assert (q1 | q2) == query.MatchAll()
    assert (q2 | q1) == query.MatchAll()


def test_or_produces_bool_with_should():
    q1 = query.Match(f=42)
    q2 = query.Match(g="v")

    q = q1 | q2
    assert q == query.Bool(should=[q1, q2])


def test_or_bool_doesnt_loop_infinitely_issue_37():
    q = query.Match(f=42) | ~query.Match(f=47)

    assert q == query.Bool(
        should=[query.Bool(must_not=[query.Match(f=47)]), query.Match(f=42)]
    )


def test_or_bool_doesnt_loop_infinitely_issue_96():
    q = ~query.Match(f=42) | ~query.Match(f=47)

    assert q == query.Bool(
        should=[
            query.Bool(must_not=[query.Match(f=42)]),
            query.Bool(must_not=[query.Match(f=47)]),
        ]
    )


def test_bool_will_append_another_query_with_or():
    qb = query.Bool(should=[query.Match(f="v"), query.Match(f="v2")])
    q = query.Match(g=42)

    assert (q | qb) == query.Bool(should=[query.Match(f="v"), query.Match(f="v2"), q])


def test_bool_queries_with_only_should_get_concatenated():
    q1 = query.Bool(should=[query.Match(f=1), query.Match(f=2)])
    q2 = query.Bool(should=[query.Match(f=3), query.Match(f=4)])

    assert (q1 | q2) == query.Bool(
        should=[query.Match(f=1), query.Match(f=2), query.Match(f=3), query.Match(f=4)]
    )


def test_two_bool_queries_append_one_to_should_if_possible():
    q1 = query.Bool(should=[query.Match(f="v")])
    q2 = query.Bool(must=[query.Match(f="v")])

    assert (q1 | q2) == query.Bool(
        should=[query.Match(f="v"), query.Bool(must=[query.Match(f="v")])]
    )
    assert (q2 | q1) == query.Bool(
        should=[query.Match(f="v"), query.Bool(must=[query.Match(f="v")])]
    )


def test_queries_are_registered():
    assert "match" in query.Query._classes
    assert query.Query._classes["match"] is query.Match


def test_defining_query_registers_it():
    class MyQuery(query.Query):
        name = "my_query"

    assert "my_query" in query.Query._classes
    assert query.Query._classes["my_query"] is MyQuery


def test_Q_passes_query_through():
    q = query.Match(f="value1")

    assert query.Q(q) is q


def test_Q_constructs_query_by_name():
    q = query.Q("match", f="value")

    assert isinstance(q, query.Match)
    assert {"f": "value"} == q._params


def test_Q_translates_double_underscore_to_dots_in_param_names():
    q = query.Q("match", comment__author="honza")

    assert {"comment.author": "honza"} == q._params


def test_Q_doesn_translate_double_underscore_to_dots_in_param_names():
    q = query.Q("match", comment__author="honza", _expand__to_dot=False)

    assert {"comment__author": "honza"} == q._params


def test_Q_constructs_simple_query_from_dict():
    q = query.Q({"match": {"f": "value"}})

    assert isinstance(q, query.Match)
    assert {"f": "value"} == q._params


def test_Q_constructs_compound_query_from_dict():
    q = query.Q({"bool": {"must": [{"match": {"f": "value"}}]}})

    assert q == query.Bool(must=[query.Match(f="value")])


def test_Q_raises_error_when_passed_in_dict_and_params():
    with raises(Exception):
        query.Q({"match": {"f": "value"}}, f="value")


def test_Q_raises_error_when_passed_in_query_and_params():
    q = query.Match(f="value1")

    with raises(Exception):
        query.Q(q, f="value")


def test_Q_raises_error_on_unknown_query():
    with raises(Exception):
        query.Q("not a query", f="value")


def test_match_all_and_anything_is_anything():
    q = query.MatchAll()

    s = query.Match(f=42)
    assert q & s == s
    assert s & q == s


def test_function_score_with_functions():
    q = query.Q(
        "function_score",
        functions=[query.SF("script_score", script="doc['comment_count'] * _score")],
    )

    assert {
        "function_score": {
            "functions": [{"script_score": {"script": "doc['comment_count'] * _score"}}]
        }
    } == q.to_dict()


def test_function_score_with_no_function_is_boost_factor():
    q = query.Q(
        "function_score",
        functions=[query.SF({"weight": 20, "filter": query.Q("term", f=42)})],
    )

    assert {
        "function_score": {"functions": [{"filter": {"term": {"f": 42}}, "weight": 20}]}
    } == q.to_dict()


def test_function_score_to_dict():
    q = query.Q(
        "function_score",
        query=query.Q("match", title="python"),
        functions=[
            query.SF("random_score"),
            query.SF(
                "field_value_factor",
                field="comment_count",
                filter=query.Q("term", tags="python"),
            ),
        ],
    )

    d = {
        "function_score": {
            "query": {"match": {"title": "python"}},
            "functions": [
                {"random_score": {}},
                {
                    "filter": {"term": {"tags": "python"}},
                    "field_value_factor": {"field": "comment_count"},
                },
            ],
        }
    }
    assert d == q.to_dict()


def test_function_score_with_single_function():
    d = {
        "function_score": {
            "filter": {"term": {"tags": "python"}},
            "script_score": {"script": "doc['comment_count'] * _score"},
        }
    }

    q = query.Q(d)
    assert isinstance(q, query.FunctionScore)
    assert isinstance(q.filter, query.Term)
    assert len(q.functions) == 1

    sf = q.functions[0]
    assert isinstance(sf, function.ScriptScore)
    assert "doc['comment_count'] * _score" == sf.script


def test_function_score_from_dict():
    d = {
        "function_score": {
            "filter": {"term": {"tags": "python"}},
            "functions": [
                {
                    "filter": {"terms": {"tags": "python"}},
                    "script_score": {"script": "doc['comment_count'] * _score"},
                },
                {"boost_factor": 6},
            ],
        }
    }

    q = query.Q(d)
    assert isinstance(q, query.FunctionScore)
    assert isinstance(q.filter, query.Term)
    assert len(q.functions) == 2

    sf = q.functions[0]
    assert isinstance(sf, function.ScriptScore)
    assert isinstance(sf.filter, query.Terms)

    sf = q.functions[1]
    assert isinstance(sf, function.BoostFactor)
    assert 6 == sf.value
    assert {"boost_factor": 6} == sf.to_dict()
