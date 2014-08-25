from elasticsearch_dsl import filter

def test_and_can_be_created_with_a_list():
    f = filter.F('and', [filter.F('term', field='value')])

    assert isinstance(f, filter.And)
    assert f.filters == [filter.F('term', field='value')]

def test_not_doesnt_have_to_wrap_filter():
    f = filter.F('not', term={'field': 'value'})

    assert isinstance(f, filter.Not)
    assert f.filter == filter.F('term', field='value')
