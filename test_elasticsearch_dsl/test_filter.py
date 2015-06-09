from elasticsearch_dsl import filter, Q

from pytest import raises

def test_repr():
    f = filter.F('terms', **{'some.path': 'value'})

    assert "Terms(some__path='value')" == repr(f)

def test_and_can_be_created_from_list():
    f = filter.F({'and': [{'term': {'f': 'v'}}, {'term': {'f2': 42}}]})

    assert f == filter.And([filter.F('term', f='v'), filter.F('term', f2=42)])

def test_empty_F_is_match_all():
    f = filter.F()

    assert isinstance(f, filter.MatchAll)
    assert filter.MatchAll() == f

def test_and_can_be_created_with_a_list():
    f = filter.F('and', [filter.F('term', field='value')])

    assert isinstance(f, filter.And)
    assert f.filters == [filter.F('term', field='value')]
    assert f == filter.And([filter.F('term', field='value')])

def test_other_filters_must_use_kwargs():
    with raises(ValueError):
        filter.F('bool', [filter.F('term', field='value')])

def test_not_doesnt_have_to_wrap_filter():
    f = filter.F('not', term={'field': 'value'})

    assert isinstance(f, filter.Not)
    assert f.filter == filter.F('term', field='value')
    assert f == filter.Not(filter.F('term', field='value'))

def test_query_can_use_positional_arg():
    f = filter.F('query', Q('match_all'))

    assert f.query == Q('match_all')
    assert {'query': {'match_all': {}}} == f.to_dict()
