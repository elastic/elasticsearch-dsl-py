from datetime import datetime, timedelta

from elasticsearch_dsl import Range

import pytest

@pytest.mark.parametrize('kwargs, item', [
    ({}, 1),
    ({}, -1),
    ({'gte': -1}, -1),
    ({'lte': 4}, 4),
    ({'lte': 4, 'gte': 2}, 4),
    ({'lte': 4, 'gte': 2}, 2),
    ({'gt': datetime.now() - timedelta(seconds=10)}, datetime.now())

])
def test_range_contains(kwargs, item):
    assert item in Range(**kwargs)

@pytest.mark.parametrize('kwargs, item', [
    ({'gt': -1}, -1),
    ({'lt': 4}, 4),
    ({'lt': 4}, 42),
    ({'lte': 4, 'gte': 2}, 1),
    ({'lte': datetime.now() - timedelta(seconds=10)}, datetime.now())
])
def test_range_not_contains(kwargs, item):
    assert item not in Range(**kwargs)

@pytest.mark.parametrize('args,kwargs', [
    (({}, ), {'lt': 42}),
    ((), {'not_lt': 42}),
    ((object(),), {}),
    ((), {'lt': 1, 'lte': 1}),
    ((), {'gt': 1, 'gte': 1}),
])
def test_range_raises_value_error_on_wrong_params(args, kwargs):
    with pytest.raises(ValueError):
        Range(*args, **kwargs)

@pytest.mark.parametrize('range,lower,inclusive', [
    (Range(gt=1), 1, False),
    (Range(gte=1), 1, True),
    (Range(), None, False),
    (Range(lt=42), None, False),
])
def test_range_lower(range, lower, inclusive):
    assert (lower, inclusive) == range.lower

@pytest.mark.parametrize('range,upper,inclusive', [
    (Range(lt=1), 1, False),
    (Range(lte=1), 1, True),
    (Range(), None, False),
    (Range(gt=42), None, False),
])
def test_range_upper(range, upper, inclusive):
    assert (upper, inclusive) == range.upper
