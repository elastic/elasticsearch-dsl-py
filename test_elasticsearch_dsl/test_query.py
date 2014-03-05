from elasticsearch_dsl import query

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

