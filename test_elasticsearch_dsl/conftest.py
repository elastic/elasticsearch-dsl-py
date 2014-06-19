import os

from elasticsearch.helpers.test import get_test_client, SkipTest
from elasticsearch.helpers import bulk

from pytest import fixture, skip

from .test_integration.test_data import DATA, create_git_index

_client_loaded = False

@fixture(scope='session')
def client(request):
    # hack to workaround pytest not caching skip on fixtures (#467)
    global _client_loaded
    if _client_loaded:
        skip()

    _client_loaded = True
    try:
        return get_test_client(nowait='WAIT_FOR_ES' not in os.environ)
    except SkipTest:
        skip()

@fixture(scope='session')
def data_client(request, client):
    # create mappings
    create_git_index(client, 'git')
    # load data
    bulk(client, DATA, raise_on_error=True, refresh=True)
    # make sure we clean up after ourselves
    request.addfinalizer(lambda: client.indices.delete('git'))
    return client

@fixture
def dummy_response():
    return {
      "_shards": {
        "failed": 0,
        "successful": 10,
        "total": 10
      },
      "hits": {
        "hits": [
          {
            "_index": "test-index",
            "_type": "company",
            "_id": "elasticsearch",
            "_score": 12.0,

            "_source": {
              "city": "Amsterdam",
              "name": "Elasticsearch",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "42",
            "_score": 11.123,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Shay",
                "last": "Bannon"
              },
              "lang": "java",
              "twitter": "kimchy",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "47",
            "_score": 1,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Honza",
                "last": "Král"
              },
              "lang": "python",
              "twitter": "honzakral",
            },
          },
        ],
        "max_score": 12.0,
        "total": 123
      },
      "timed_out": False,
      "took": 123
    }

