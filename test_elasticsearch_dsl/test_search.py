from elasticsearch_dsl import search, query

def test_search_starts_with_empty_query():
    s = search.Search()

    assert s.query._query == query.MatchAll()

def test_search_query_combines_query():
    s = search.Search()

    assert s is s.query('match', f=42)
    assert s.query._query == query.Match(f=42)

    assert s is s.query('match', f=43)
    assert s.query._query == query.Bool(must=[query.Match(f=42), query.Match(f=43)])

def test_search_query_accepts_operator():
    s = search.Search()

    s.query('match', f=42, operator='not')
    assert s.query._query == query.Bool(must_not=[query.Match(f=42)])

    s.query('match', g='v')
    assert s.query._query == query.Bool(must_not=[query.Match(f=42)], must=[query.Match(g='v')])

    s.query('bool', must=[{"match": {"f2": "v2"}}], operator='and')
    assert s.query._query == query.Bool(must=[
        query.Bool(must_not=[query.Match(f=42)], must=[query.Match(g='v')]),
        query.Bool(must=[query.Match(f2="v2")])
    ])

def test_methods_are_proxied_to_the_query():
    s = search.Search()

    assert s.query.to_dict() == {'match_all': {}}

def test_query_always_returns_search():
    s = search.Search()

    assert s.query('match', f=42) is s

def test_search_index():
    s = search.Search(index='i')
    assert s._index == ['i']
    s.index('i2')
    assert s._index == ['i', 'i2']
    s.index()
    assert s._index is None
    s = search.Search(index=('i', 'i2'))
    assert s._index == ['i', 'i2']
    s = search.Search(index=['i', 'i2'])
    assert s._index == ['i', 'i2']
    s = search.Search()
    s.index('i', 'i2')
    assert s._index == ['i', 'i2']

def test_search_doc_type():
    s = search.Search(doc_type='i')
    assert s._doc_type == ['i']
    s.doc_type('i2')
    assert s._doc_type == ['i', 'i2']
    s.doc_type()
    assert s._doc_type is None
    s = search.Search(doc_type=('i', 'i2'))
    assert s._doc_type == ['i', 'i2']
    s = search.Search(doc_type=['i', 'i2'])
    assert s._doc_type == ['i', 'i2']
    s = search.Search()
    s.doc_type('i', 'i2')
    assert s._doc_type == ['i', 'i2']

def test_search_to_dict():
    s = search.Search()
    assert {"query": {"match_all": {}}} == s.to_dict()

    s.query('match', f=42)
    assert {"query": {"match": {'f': 42}}} == s.to_dict()

    assert {"query": {"match": {'f': 42}}, "size": 10} == s.to_dict(size=10)

    s.aggs.bucket('per_tag', 'terms', field='f').aggregate('max_score', 'max', field='score')
    d = {
        'aggs': {
            'per_tag': {
                'terms': {'field': 'f'},
                'aggs': {'max_score': {'max': {'field': 'score'}}}
             }
        },
        'query': {'match': {'f': 42}}
    }
    assert d == s.to_dict()
