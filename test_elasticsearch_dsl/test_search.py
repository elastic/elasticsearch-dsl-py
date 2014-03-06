from elasticsearch_dsl import search, query

def test_search_starts_with_empty_query():
    s = search.Search()

    assert s.query._query == query.MatchAll()

def test_search_query_combines_query():
    s = search.Search()

    s.query('match', f=42)
    assert s.query._query == query.MatchQuery(f=42)

    s.query('match', f=43)
    assert s.query._query == query.BoolQuery(must=[query.MatchQuery(f=42), query.MatchQuery(f=43)])

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

