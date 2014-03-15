from elasticsearch_dsl import query

from pytest import raises

def test_match_to_dict():
    assert {"match": {"f": "value"}} == query.Match(f='value').to_dict()

def test_bool_to_dict():
    bool = query.Bool(must=[query.Match(f='value')])

    assert {"bool": {"must": [{"match": {"f": "value"}}]}} == bool.to_dict()

def test_bool_converts_its_init_args_to_queries():
    q = query.Bool(must=[{"match": {"f": "value"}}])

    assert len(q.must) == 1
    assert q.must[0] == query.Match(f='value')

def test_two_queries_make_a_bool():
    q1 = query.Match(f='value1')
    q2 = query.Match(message={"query": "this is a test", "opeartor": "and"})
    q = q1 + q2

    assert isinstance(q, query.Bool)
    assert [q1, q2] == q.must

def test_other_and_bool_appends_other_to_must():
    q1 = query.Match(f='value1')
    qb = query.Bool()

    q = q1 + qb
    assert q is qb
    assert q.must[0] is q1

def test_bool_and_other_appends_other_to_must():
    q1 = query.Match(f='value1')
    qb = query.Bool()

    q = qb + q1
    assert q is qb
    assert q.must[0] is q1

def test_queries_are_registered():
    assert 'match' in query.QueryMeta._classes
    assert query.QueryMeta._classes['match'] is query.Match

def test_defining_query_registers_it():
    class MyQuery(query.Query):
        name = 'my_query'

    assert 'my_query' in query.QueryMeta._classes
    assert query.QueryMeta._classes['my_query'] is MyQuery

def test_Q_passes_query_through():
    q = query.Match(f='value1')

    assert query.Q(q) is q

def test_Q_constructs_query_by_name():
    q = query.Q('match', f='value')

    assert isinstance(q, query.Match)
    assert {'f': 'value'} == q._params

def test_Q_constructs_simple_query_from_dict():
    q = query.Q({'match': {'f': 'value'}})

    assert isinstance(q, query.Match)
    assert {'f': 'value'} == q._params

def test_Q_constructs_compound_query_from_dict():
    q = query.Q(
        {
            "bool": {
                "must": [
                    {'match': {'f': 'value'}},
                ]
            }
        }
    )

    assert q == query.Bool(must=[query.Match(f='value')])

def test_Q_raises_error_when_passed_in_dict_and_params():
    with raises(Exception):
        query.Q({"match": {'f': 'value'}}, f='value')

def test_Q_raises_error_when_passed_in_query_and_params():
    q = query.Match(f='value1')

    with raises(Exception):
        query.Q(q, f='value')

def test_Q_raises_error_on_unknown_query():
    with raises(Exception):
        query.Q('not a query', f='value')

def test_match_all_plus_anything_is_anything():
    q = query.MatchAll()

    s = object()
    assert q+s is s
    assert s+q is s
