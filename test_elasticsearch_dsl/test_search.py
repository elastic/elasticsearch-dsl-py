from copy import deepcopy

from elasticsearch_dsl import search, query, F, Q, DocType, utils


def test_execute_uses_cache():
    s = search.Search()
    r = object()
    s._response = r

    assert r is s.execute()

def test_cache_can_be_ignored(mock_client):
    s = search.Search(using='mock')
    r = object()
    s._response = r
    s.execute(ignore_cache=True)

    mock_client.search.assert_called_once_with(
        doc_type=[],
        index=None,
        body={'query': {'match_all': {}}},
    )

def test_iter_iterates_over_hits():
    s = search.Search()
    s._response = [1, 2, 3]

    assert [1, 2, 3] == list(s)

def test_count_uses_cache():
    s = search.Search()
    s._response = utils.AttrDict({'hits': {'total': 42}})

    assert 42 == s.count()

def test_cache_isnt_cloned():
    s = search.Search()
    s._response = object()

    assert not hasattr(s._clone(), '_response')


def test_search_starts_with_empty_query():
    s = search.Search()

    assert s.query._proxied == query.MatchAll()

def test_search_query_combines_query():
    s = search.Search()

    s2 = s.query('match', f=42)
    assert s2.query._proxied == query.Match(f=42)
    assert s.query._proxied == query.MatchAll()

    s3 = s2.query('match', f=43)
    assert s2.query._proxied == query.Match(f=42)
    assert s3.query._proxied == query.Bool(must=[query.Match(f=42), query.Match(f=43)])

def test_query_can_be_assigned_to():
    s = search.Search()

    q = Q('match', title='python')
    s.query = q

    assert s.query._proxied is q

def test_query_can_be_wrapped():
    s = search.Search().query('match', title='python')

    s.query = Q('function_score', query=s.query, field_value_factor={'field': 'rating'})

    assert {
        'query': {
            'function_score': {
                'functions': [{'field_value_factor': {'field': 'rating'}}],
                'query': {'match': {'title': 'python'}}
            }
        }
    }== s.to_dict()

def test_filter_can_be_overriden():
    s = search.Search().filter('term', tag='python')
    s.filter = ~F(s.filter)

    assert {
        "query": {
            "filtered": {
                "query": {"match_all": {}},
                "filter": {"bool": {"must_not": [{"term": {"tag": "python"}}]}}
            }
        }
    } == s.to_dict()

def test_using():
    o = object()
    o2 = object()
    s = search.Search(using=o)
    assert s._using is o
    s2 = s.using(o2)
    assert s._using is o
    assert s2._using is o2

def test_methods_are_proxied_to_the_query():
    s = search.Search()

    assert s.query.to_dict() == {'match_all': {}}

def test_query_always_returns_search():
    s = search.Search()

    assert isinstance(s.query('match', f=42), search.Search)

def test_aggs_get_copied_on_change():
    s = search.Search()
    s.aggs.bucket('per_tag', 'terms', field='f').metric('max_score', 'max', field='score')

    s2 = s.query('match_all')
    s2.aggs.bucket('per_month', 'date_histogram', field='date', interval='month')
    s3 = s2.query('match_all')
    s3.aggs['per_month'].metric('max_score', 'max', field='score')
    s4 = s3._clone()
    s4.aggs.metric('max_score', 'max', field='score')

    d = {
        'query': {'match_all': {}},
        'aggs': {
            'per_tag': {
                'terms': {'field': 'f'},
                'aggs': {'max_score': {'max': {'field': 'score'}}}
             }
        }
    }

    assert d == s.to_dict()
    d['aggs']['per_month'] = {"date_histogram": {'field': 'date', 'interval': 'month'}}
    assert d == s2.to_dict()
    d['aggs']['per_month']['aggs'] = {"max_score": {"max": {"field": 'score'}}}
    assert d == s3.to_dict()
    d['aggs']['max_score'] = {"max": {"field": 'score'}}
    assert d == s4.to_dict()

def test_search_index():
    s = search.Search(index='i')
    assert s._index == ['i']
    s = s.index('i2')
    assert s._index == ['i', 'i2']
    s = s.index()
    assert s._index is None
    s = search.Search(index=('i', 'i2'))
    assert s._index == ['i', 'i2']
    s = search.Search(index=['i', 'i2'])
    assert s._index == ['i', 'i2']
    s = search.Search()
    s = s.index('i', 'i2')
    assert s._index == ['i', 'i2']
    s2 = s.index('i3')
    assert s._index == ['i', 'i2']
    assert s2._index == ['i', 'i2', 'i3']

def test_search_doc_type():
    s = search.Search(doc_type='i')
    assert s._doc_type == ['i']
    s = s.doc_type('i2')
    assert s._doc_type == ['i', 'i2']
    s = s.doc_type()
    assert s._doc_type == []
    s = search.Search(doc_type=('i', 'i2'))
    assert s._doc_type == ['i', 'i2']
    s = search.Search(doc_type=['i', 'i2'])
    assert s._doc_type == ['i', 'i2']
    s = search.Search()
    s = s.doc_type('i', 'i2')
    assert s._doc_type == ['i', 'i2']
    s2 = s.doc_type('i3')
    assert s._doc_type == ['i', 'i2']
    assert s2._doc_type == ['i', 'i2', 'i3']


def test_doc_type_can_be_document_class():
    class MyDocType(DocType):
        pass

    s = search.Search(doc_type=MyDocType)
    assert s._doc_type == ['my_doc_type']
    assert s._doc_type_map == {'my_doc_type': MyDocType.from_es}

    s = search.Search().doc_type(MyDocType)
    assert s._doc_type == ['my_doc_type']
    assert s._doc_type_map == {'my_doc_type': MyDocType.from_es}


def test_sort():
    s = search.Search()
    s = s.sort('fielda', '-fieldb')

    assert ['fielda', {'fieldb': {'order': 'desc'}}] == s._sort
    assert {'query': {'match_all': {}}, 'sort': ['fielda', {'fieldb': {'order': 'desc'}}]} == s.to_dict()

    s = s.sort()
    assert [] == s._sort
    assert search.Search().to_dict() == s.to_dict()

def test_slice():
    s = search.Search()
    assert {'query': {'match_all': {}}, 'from': 3, 'size': 7} == s[3:10].to_dict()
    assert {'query': {'match_all': {}}, 'from': 0, 'size': 5} == s[:5].to_dict()
    assert {'query': {'match_all': {}}, 'from': 3, 'size': 10} == s[3:].to_dict()
    assert {'query': {'match_all': {}}, 'from': 0, 'size': 0} == s[0:0].to_dict()

def test_index():
    s = search.Search()
    assert {'query': {'match_all': {}}, 'from': 3, 'size': 1} == s[3].to_dict()

def test_search_to_dict():
    s = search.Search()
    assert {"query": {"match_all": {}}} == s.to_dict()

    s = s.query('match', f=42)
    assert {"query": {"match": {'f': 42}}} == s.to_dict()

    assert {"query": {"match": {'f': 42}}, "size": 10} == s.to_dict(size=10)

    s.aggs.bucket('per_tag', 'terms', field='f').metric('max_score', 'max', field='score')
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

    s = search.Search(extra={"size": 5})
    assert {"query": {"match_all": {}}, "size": 5} == s.to_dict()
    s = s.extra(from_=42)
    assert {"query": {"match_all": {}}, "size": 5, "from": 42} == s.to_dict()


def test_complex_example():
    s = search.Search()
    s = s.query('match', title='python') \
        .query(~Q('match', title='ruby')) \
        .filter(F('term', category='meetup') | F('term', category='conference')) \
        .post_filter('terms', tags=['prague', 'czech']) \
        .script_fields(more_attendees="doc['attendees'].value + 42")

    s.aggs.bucket('per_country', 'terms', field='country')\
        .metric('avg_attendees', 'avg', field='attendees')

    s.query.minimum_should_match = 2

    s = s.highlight_options(order='score').highlight('title', 'body', fragment_size=50)

    assert {
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
        'post_filter': {
            'terms': {'tags': ['prague', 'czech']}
        },
        'aggs': {
            'per_country': {
                'terms': {'field': 'country'},
                'aggs': {
                    'avg_attendees': {'avg': {'field': 'attendees'}}
                }
            }
        },
        "highlight": {
            'order': 'score',
            'fields': {
                'title': {'fragment_size': 50},
                'body': {'fragment_size': 50}
            }
        },
        'script_fields': {
            'more_attendees': {'script': "doc['attendees'].value + 42"}
        }
    } == s.to_dict()

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
        'post_filter': {
            'bool': {'must': [{'terms': {'tags': ['prague', 'czech']}}]}
        },
        'aggs': {
            'per_country': {
                'terms': {'field': 'country'},
                'aggs': {
                    'avg_attendees': {'avg': {'field': 'attendees'}}
                }
            }
        },
        "sort": [
            "title",
            {"category": {"order": "desc"}},
            "_score"
        ],
        "fields": [
            "category",
            "title"
        ],
        "size": 5,
        "highlight": {
            'order': 'score',
            'fields': {
                'title': {'fragment_size': 50}
            }
        },
        "suggest": {
            "my-title-suggestions-1" : {
                "text" : "devloping distibutd saerch engies",
                "term" : {
                    "size" : 3,
                    "field" : "title"
                }
            }
        },
        'script_fields': {
            'more_attendees': {'script': "doc['attendees'].value + 42"}
        }
    }

    d2 = deepcopy(d)

    s = search.Search.from_dict(d)

    # make sure we haven't modified anything in place
    assert d == d2
    assert {"size": 5} == s._extra
    assert d == s.to_dict()

def test_from_dict_doesnt_need_query():
    s = search.Search.from_dict({"size": 5})

    assert {
        "query": {"match_all": {}},
        "size": 5
    } == s.to_dict()

def test_params_being_passed_to_search(mock_client):
    s = search.Search(using='mock')
    s = s.params(routing='42')
    s.execute()

    mock_client.search.assert_called_once_with(
        doc_type=[],
        index=None,
        body={'query': {'match_all': {}}},
        routing='42'
    )

def test_fields():
    assert {
        'query': {
            'match_all': {}
        },
        'fields': ['title']
    } == search.Search().fields(['title']).to_dict()
    assert {
        'query': {
            'match_all': {}
        },
        'fields': ['id', 'title']
    } == search.Search().fields(['id', 'title']).to_dict()
    assert {
        'query': {
            'match_all': {}
        },
        'fields': []
    } == search.Search().fields([]).to_dict()
    assert {
        'query': {
            'match_all': {}
        }
    } == search.Search().fields().to_dict()
    assert {
        'query': {
            'match_all': {}
        }
    } == search.Search().fields(None).to_dict()

def test_fields_on_clone():
    assert {
        'query': {
            'filtered': {
                'filter': {'term': {'title': 'python'}},
                'query': {'match_all': {}}
            }
        },
        'fields': ['title']
    } == search.Search().fields(['title']).filter('term', title='python').to_dict()

def test_partial_fields():
    assert {
        'query': {
            'match_all': {}
        },
    } == search.Search().partial_fields().to_dict()

    assert {
        'query': {
            'match_all': {}
        },
        'partial_fields': {
            'foo': {
                'include': ['foo.bar.*'],
                'exclude': ['foo.one']
            }
        }
    } == search.Search().partial_fields(foo={
        'include': ['foo.bar.*'],
        'exclude': ['foo.one']
    }).to_dict()

    assert {
        'query': {
            'match_all': {}
        },
        'partial_fields': {
            'foo': {
                'include': ['foo.bar.*'],
                'exclude': ['foo.one'],
            },
            'bar': {
                'include': ['bar.bar.*'],
            }
        }
    } == search.Search().partial_fields(foo={
        'include': ['foo.bar.*'],
        'exclude': ['foo.one']
    }, bar={
        'include': ['bar.bar.*']
    }).to_dict()

    assert {
        'query': {
            'match_all': {}
        },
        'partial_fields': {
            'bar': {
                'include': ['bar.*'],
            }
        }
    } == search.Search().partial_fields(foo={
        'include': ['foo.bar.*']
    }).partial_fields(bar={
        'include': ['bar.*']
    }).to_dict()

def test_partial_fields_on_clone():
    assert {
        'query': {
            'filtered': {
                'filter': {
                    'term': {
                        'title': 'python',
                    }
                },
                'query': {
                    'match_all': {},
                }
            }
        },
        'partial_fields': {
            'foo': {
                'include': ['foo.bar.*'],
                'exclude': ['foo.one']
            }
        }
    } == search.Search().partial_fields(foo={
        'include': ['foo.bar.*'],
        'exclude': ['foo.one']
    }).filter('term', title='python').to_dict()

def test_suggest_accepts_global_text():
    s = search.Search.from_dict({
        "query": {"match_all": {}},
        "suggest" : {
            "text" : "the amsterdma meetpu",
            "my-suggest-1" : {
                "term" : {"field" : "title"}
            },
            "my-suggest-2" : {
                "text": "other",
                "term" : {"field" : "body"}
            }
        }
    })

    assert {
        'query': {'match_all': {}},
        'suggest': {
            'my-suggest-1': {
                'term': {'field': 'title'},
                'text': 'the amsterdma meetpu'
            },
            'my-suggest-2': {
                'term': {'field': 'body'},
                'text': 'other'}
        }
    } == s.to_dict()

def test_suggest():
    s = search.Search()
    s = s.suggest('my_suggestion', 'pyhton', term={'field': 'title'})

    assert {
        'query': {'match_all': {}},
        'suggest': {
            'my_suggestion': {
                'term': {'field': 'title'},
                'text': 'pyhton'
            }
        }
    } == s.to_dict()
