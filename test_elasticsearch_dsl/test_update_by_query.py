from copy import deepcopy

from elasticsearch_dsl import UpdateByQuery, query, Q, Document


# A lot of the basic query testing for Search can be copied over here and re-used
def test_expand__to_dot_is_respected():
    ubq = UpdateByQuery().query('match', a__b=42, _expand__to_dot=False)

    assert {"query": {"match": {"a__b": 42}}} == ubq.to_dict()

def test_cache_isnt_cloned():
    ubq = UpdateByQuery()
    ubq._response = object()

    assert not hasattr(ubq._clone(), '_response')

def test_ubq_starts_with_no_query():
    ubq = UpdateByQuery()

    assert ubq.query._proxied is None

def test_ubq_combines_query():
    ubq = UpdateByQuery()

    ubq2 = ubq.query('match', f=42)
    assert ubq2.query._proxied == query.Match(f=42)
    assert ubq.query._proxied is None

    ubq3 = ubq2.query('match', f=43)
    assert ubq2.query._proxied == query.Match(f=42)
    assert ubq3.query._proxied == query.Bool(must=[query.Match(f=42), query.Match(f=43)])

def test_query_can_be_assigned_to():
    ubq = UpdateByQuery()

    q = Q('match', title='python')
    ubq.query = q

    assert ubq.query._proxied is q

def test_query_can_be_wrapped():
    ubq = UpdateByQuery().query('match', title='python')

    ubq.query = Q('function_score', query=ubq.query, field_value_factor={'field': 'rating'})

    assert {
        'query': {
            'function_score': {
                'functions': [{'field_value_factor': {'field': 'rating'}}],
                'query': {'match': {'title': 'python'}}
            }
        }
    } == ubq.to_dict()

def test_using():
    o = object()
    o2 = object()
    ubq = UpdateByQuery(using=o)
    assert ubq._using is o
    ubq2 = ubq.using(o2)
    assert ubq._using is o
    assert ubq2._using is o2

def test_methods_are_proxied_to_the_query():
    ubq = UpdateByQuery().query('match_all')

    assert ubq.query.to_dict() == {'match_all': {}}

def test_query_always_returns_ubq():
    ubq = UpdateByQuery()

    assert isinstance(ubq.query('match', f=42), UpdateByQuery)

def test_copy_clones():
    from copy import copy
    ubq1 = UpdateByQuery().query('match', f=42)
    ubq2 = copy(ubq1)

    assert ubq1 == ubq2
    assert ubq1 is not ubq2

def test_ubq_index():
    ubq = UpdateByQuery(index='i')
    assert ubq._index == ['i']
    ubq = ubq.index('i2')
    assert ubq._index == ['i', 'i2']
    ubq = ubq.index(u'i3')
    assert ubq._index == ['i', 'i2', 'i3']
    ubq = ubq.index()
    assert ubq._index is None
    ubq = UpdateByQuery(index=('i', 'i2'))
    assert ubq._index == ['i', 'i2']
    ubq = UpdateByQuery(index=['i', 'i2'])
    assert ubq._index == ['i', 'i2']
    ubq = UpdateByQuery()
    ubq = ubq.index('i', 'i2')
    assert ubq._index == ['i', 'i2']
    ubq2 = ubq.index('i3')
    assert ubq._index == ['i', 'i2']
    assert ubq2._index == ['i', 'i2', 'i3']
    ubq = UpdateByQuery()
    ubq = ubq.index(['i', 'i2'], 'i3')
    assert ubq._index == ['i', 'i2', 'i3']
    ubq2 = ubq.index('i4')
    assert ubq._index == ['i', 'i2', 'i3']
    assert ubq2._index == ['i', 'i2', 'i3', 'i4']
    ubq2 = ubq.index(['i4'])
    assert ubq2._index == ['i', 'i2', 'i3', 'i4']
    ubq2 = ubq.index(('i4', 'i5'))
    assert ubq2._index == ['i', 'i2', 'i3', 'i4', 'i5']

def test_ubq_doc_type():
    ubq = UpdateByQuery(doc_type='i')
    assert ubq._doc_type == ['i']
    ubq = ubq.doc_type('i2')
    assert ubq._doc_type == ['i', 'i2']
    ubq = ubq.doc_type()
    assert ubq._doc_type == []
    ubq = UpdateByQuery(doc_type=('i', 'i2'))
    assert ubq._doc_type == ['i', 'i2']
    ubq = UpdateByQuery(doc_type=['i', 'i2'])
    assert ubq._doc_type == ['i', 'i2']
    ubq = UpdateByQuery()
    ubq = ubq.doc_type('i', 'i2')
    assert ubq._doc_type == ['i', 'i2']
    ubq2 = ubq.doc_type('i3')
    assert ubq._doc_type == ['i', 'i2']
    assert ubq2._doc_type == ['i', 'i2', 'i3']

def test_doc_type_can_be_document_class():
    class MyDocument(Document):
        pass

    ubq = UpdateByQuery(doc_type=MyDocument)
    assert ubq._doc_type == [MyDocument]
    assert ubq._doc_type_map == {}
    assert ubq._get_doc_type() == ['doc']

    ubq = UpdateByQuery().doc_type(MyDocument)
    assert ubq._doc_type == [MyDocument]
    assert ubq._doc_type_map == {}
    assert ubq._get_doc_type() == ['doc']

def test_search_to_dict():
    ubq = UpdateByQuery()
    assert {} == ubq.to_dict()

    ubq = ubq.query('match', f=42)
    assert {"query": {"match": {'f': 42}}} == ubq.to_dict()

    assert {"query": {"match": {'f': 42}}, "size": 10} == ubq.to_dict(size=10)

    ubq = UpdateByQuery(extra={"size": 5})
    assert {"size": 5} == ubq.to_dict()

def test_complex_example():
    ubq = UpdateByQuery()
    ubq = ubq.query('match', title='python') \
        .query(~Q('match', title='ruby')) \
        .filter(Q('term', category='meetup') | Q('term', category='conference')) \
        .script(source='ctx._source.likes += params.f', lang='painless', params={'f': 3})

    ubq.query.minimum_should_match = 2
    assert {
        'query': {
            'bool': {
                'filter': [
                    {
                        'bool': {
                            'should': [
                                {'term': {'category': 'meetup'}},
                                {'term': {'category': 'conference'}}
                            ]
                        }
                    }
                ],
                'must': [ {'match': {'title': 'python'}}],
                'must_not': [{'match': {'title': 'ruby'}}],
                'minimum_should_match': 2
            }
        },
        'script': {
            'source': 'ctx._source.likes += params.f',
            'lang': 'painless',
            'params': {
                'f': 3
            }
        }
    } == ubq.to_dict()

def test_reverse():
    d =  {
        'query': {
            'filtered': {
                'filter': {
                    'bool': {
                        'should': [
                            {'term': {'category': 'meetup'}},
                            {'term': {'category': 'conference'}}
                        ]
                    }
                },
                'query': {
                    'bool': {
                        'must': [ {'match': {'title': 'python'}}],
                        'must_not': [{'match': {'title': 'ruby'}}],
                        'minimum_should_match': 2
                    }
                }
            }
        },
        'script': {
            'source': 'ctx._source.likes += params.f',
            'lang': 'painless',
            'params': {
                'f': 3
            }
        }
    }

    d2 = deepcopy(d)

    ubq = UpdateByQuery.from_dict(d)

    # make sure we haven't modified anything in place
    assert d == d2
    assert d == ubq.to_dict()

def test_from_dict_doesnt_need_query():
    ubq = UpdateByQuery.from_dict({'script': {'source': 'test'}})

    assert {
        'script': {'source': 'test'}
    } == ubq.to_dict()

def test_params_being_passed_to_search(mock_client):
    ubq = UpdateByQuery(using='mock')
    ubq = ubq.params(routing='42')
    ubq.execute()

    mock_client.update_by_query.assert_called_once_with(
        doc_type=[],
        index=None,
        body={},
        routing='42'
    )

def test_exclude():
    ubq = UpdateByQuery()
    ubq = ubq.exclude('match', title='python')

    assert {
        'query': {
            'bool': {
                'filter': [{
                    'bool': {
                        'must_not': [{
                            'match': {
                                'title': 'python'
                            }
                        }]
                    }
                }]
            }
        }
    } == ubq.to_dict()

def test_overwrite_script():
    ubq = UpdateByQuery()
    ubq = ubq.script(source='ctx._source.likes += params.f', lang='painless', params={'f': 3})
    assert {
        'script': {
            'source': 'ctx._source.likes += params.f',
            'lang': 'painless',
            'params': {
                'f': 3
            }
        }
    } == ubq.to_dict()
    ubq = ubq.script(source='ctx._source.likes++')
    assert {
        'script': {
            'source': 'ctx._source.likes++'
        }
    } == ubq.to_dict()
