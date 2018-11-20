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
def test_contains(kwargs, item):
    assert item in Range(**kwargs)

@pytest.mark.parametrize('kwargs, item', [
    ({'gt': -1}, -1),
    ({'lt': 4}, 4),
    ({'lt': 4}, 42),
    ({'lte': 4, 'gte': 2}, 1),
    ({'lte': datetime.now() - timedelta(seconds=10)}, datetime.now())
])
def test_not_contains(kwargs, item):
    assert item not in Range(**kwargs)
