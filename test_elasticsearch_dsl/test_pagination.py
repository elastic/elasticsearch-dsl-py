from elasticsearch_dsl.search import Search

from pytest import raises

class DummySearch(Search):
    def __init__(self, *args, **kwargs):
        super(DummySearch, self).__init__(*args, **kwargs)
        self._executions = []

    def execute(self, *args, **kwargs):
        return self.to_dict()

def test_pages_are_1_based():
    body = DummySearch().get_page(1)
    assert body.get("size", 10) == 10
    assert body.get("from", 0) == 0

def test_pages_respect_page_size():
    body = DummySearch()[:6].get_page(2)
    assert body["size"] == 6
    assert body["from"] == 6

def test_get_page_doesnt_allow_0_or_negative_pages():
    with raises(ValueError):
        DummySearch().get_page(0)
    with raises(ValueError):
        DummySearch().get_page(-1)
