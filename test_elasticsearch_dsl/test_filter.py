from elasticsearch_dsl import filter

from pytest import raises

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

def test_and_filter_must_convert_nested_filters():
    f = filter.F('and', [filter.F('term', field='value')])

    assert isinstance(f, filter.And)
    assert {'and': {'filters': [{'term': {'field': 'value'}}]}} == f.to_dict()
