from elasticsearch.helpers.test import get_test_client, SkipTest
from elasticsearch.helpers import bulk

from pytest import fixture, skip

from test_integration.test_data import DATA, create_git_index

_client_loaded = False

@fixture(scope='session')
def client(request):
    # hack to workaround pytest not caching skip on fixtures (#467)
    global _client_loaded
    if _client_loaded:
        skip()

    _client_loaded = True
    try:
        return get_test_client()
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

