from copy import deepcopy

from elasticsearch_dsl import aggs

from pytest import raises

def test_A_creates_proper_agg():
    a = aggs.A('per_tag', 'terms', field='tags')

    assert isinstance(a, aggs.Terms)
    assert a._params == {'field': 'tags'}
    assert a._name == 'per_tag'

def test_A_passes_aggs_through():
    a = aggs.A('per_tag', 'terms', field='tags')
    assert aggs.A(a) is a

def test_A_from_dict():
    d = {
        'per_tag': {
            'terms': {'field': 'tags'},
            'aggs': {'per_author': {'terms': {'field': 'author.raw'}}},
        }
    }
    a = aggs.A(d)

    assert isinstance(a, aggs.Terms)
    assert a._params == {'field': 'tags', 'aggs': {'per_author': aggs.A('per_author', 'terms', field='author.raw')}}
    assert a._name == 'per_tag'
    assert a['per_author'] == aggs.A('per_author', 'terms', field='author.raw')

def test_A_fails_with_incorrect_dict():
    correct_d = {
        'per_tag': {
            'terms': {'field': 'tags'},
            'aggs': {'per_author': {'terms': {'field': 'author.raw'}}},
        }
    }

    with raises(Exception):
        aggs.A(correct_d, field='f')

    with raises(Exception):
        aggs.A(correct_d, 'name')

    d = deepcopy(correct_d)
    del d['per_tag']['terms']
    with raises(Exception):
        aggs.A(d)

    d = deepcopy(correct_d)
    d['per_tag']['xx'] = {}
    with raises(Exception):
        aggs.A(d)

    d = deepcopy(correct_d)
    d['xx'] = {}
    with raises(Exception):
        aggs.A(d)

def test_A_fails_without_agg_type():
    with raises(Exception):
        aggs.A('name', field='f')

def test_A_fails_with_agg_and_name_or_params():
    a = aggs.A('per_tag', 'terms', field='tags')

    with raises(Exception):
        aggs.A(a, 'name')

    with raises(Exception):
        aggs.A(a, field='score')

def test_buckets_are_nestable():
    a = aggs.Terms('per_tag', field='tags')
    b = a.bucket('per_author', 'terms', field='author.raw')

    assert isinstance(b, aggs.Terms)
    assert b._params == {'field': 'author.raw'}
    assert b._name == 'per_author'
    assert a.aggs == {'per_author': b}

def test_aggregate_inside_buckets():
    a = aggs.Terms('per_tag', field='tags')
    b = a.aggregate('max_score', 'max', field='score')

    # returns bucket so it's chainable
    assert a is b
    assert a.aggs['max_score'] == aggs.Max('max_score', field='score')

def test_buckets_equals_counts_subaggs():
    a = aggs.Terms('per_tag', field='tags')
    a.bucket('per_author', 'terms', field='author.raw')
    b = aggs.Terms('per_tag', field='tags')

    assert a != b

def test_buckets_to_dict():
    a = aggs.Terms('per_tag', field='tags')
    a.bucket('per_author', 'terms', field='author.raw')

    assert {
        'per_tag': {
            'terms': {'field': 'tags'},
            'aggs': {'per_author': {'terms': {'field': 'author.raw'}}},
        }
    } == a.to_dict()

    a = aggs.Terms('per_tag', field='tags')
    b = a.aggregate('max_score', 'max', field='score')

    assert {
        'per_tag': {
            'terms': {'field': 'tags'},
            'aggs': {'max_score': {'max': {'field': 'score'}}},
        }
    } == a.to_dict()

def test_nested_buckets_are_reachable_as_getitem():
    a = aggs.Terms('per_tag', field='tags')
    b = a.bucket('per_author', 'terms', field='author.raw')

    assert a['per_author'] is not b
    assert a['per_author'] == b

def test_nested_buckets_are_settable_as_getitem():
    a = aggs.Terms('per_tag', field='tags')
    b = a['per_author'] = aggs.A('per_author', 'terms', field='author.raw')

    assert a.aggs['per_author'] is b

