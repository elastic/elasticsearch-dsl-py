from elasticsearch_dsl.utils import AttrDict
from elasticsearch_dsl.search import Search

from pytest import raises

class DummySearch(Search):
    def __init__(self, *args, **kwargs):
        super(DummySearch, self).__init__(*args, **kwargs)
        self._executions = []

    def execute(self, *args, **kwargs):
        return AttrDict({
            'req': self.to_dict(),
            'hits': {
                'hits': list(range(self._extra.get('size', 10)))
            }
        })

def test_pages_are_1_based():
    body = DummySearch().get_page(1)
    assert "size" not in body['req']
    assert body['req']["from"] == 0

def test_pages_respect_page_size():
    body = DummySearch()[:6].get_page(2)
    assert body['req']["size"] == 6
    assert body['req']["from"] == 6

def test_get_page_doesnt_allow_0():
    with raises(ValueError):
        DummySearch().get_page(0)

def test_next_page_respects_size():
    body = DummySearch()[123:124].get_next_page([1, 2])
    assert body['req']["size"] == 1
    assert body['req']["from"] == 0
    assert body['req']["search_after"] == [1, 2]

def test_previous_page_reverses_sort_and_hits():
    body = DummySearch()[:5].sort(
            '_score',
            '-publish_date',
            {'author.keyword': 'asc'}
        ).get_previous_page([1, 2])

    assert body['req']["size"] == 5
    assert body['req']["from"] == 0
    assert body['req']["search_after"] == [1, 2]
    assert body['req']['sort'] == [
        {'_score': 'asc'},
        {"publish_date": {"order": "asc"}},
        {'author.keyword': 'desc'}
    ]
    assert body['hits']['hits'] == [4, 3, 2, 1, 0]
