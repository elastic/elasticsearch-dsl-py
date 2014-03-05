from elasticsearch_dsl import query

from pytest import raises

def test_match_to_dict():
    assert {"match": {"f": "value"}} == query.MatchQuery(f='value').to_dict()

def test_bool_to_dict():
    bool = query.BoolQuery(must=[query.MatchQuery(f='value')])

    assert {"bool": {"must": [{"match": {"f": "value"}}]}} == bool.to_dict()

def test_two_queries_make_a_bool():
    q1 = query.MatchQuery(f='value1')
    q2 = query.MatchQuery(message={"query": "this is a test", "opeartor": "and"})
    q = q1 + q2

    assert isinstance(q, query.BoolQuery)
    assert [q1, q2] == q.must

def test_queries_are_registered():
    assert 'match' in query.QueryMeta._queries
    assert query.QueryMeta._queries['match'] is query.MatchQuery

def test_defining_query_registers_it():
    class MyQuery(query.Query):
        name = 'my_query'

    assert 'my_query' in query.QueryMeta._queries
    assert query.QueryMeta._queries['my_query'] is MyQuery

def test_Q_passes_query_through():
    q = query.MatchQuery(f='value1')

    assert query.Q(q) is q

def test_Q_constructs_query_by_name():
    q = query.Q('match', f='value')

    assert isinstance(q, query.MatchQuery)
    assert {'f': 'value'} == q._params

def test_Q_raises_error_when_passed_in_query_and_params():
    q = query.MatchQuery(f='value1')

    with raises(Exception):
        query.Q(q, f='value')

def test_Q_raises_error_on_unknown_query():
    with raises(Exception):
        query.Q('not a query', f='value')
