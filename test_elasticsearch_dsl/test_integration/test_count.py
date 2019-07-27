from elasticsearch_dsl.search import Search, Q


def test_count_all(data_client):
    s = Search(using=data_client).index('git')
    assert 53 == s.count()


def test_count_prefetch(data_client, mocker):
    mocker.spy(data_client, 'count')

    search = Search(using=data_client).index('git')
    search.execute()
    assert search.count() == 53
    assert data_client.count.call_count == 0

    search._response.hits.total.relation = 'gte'
    assert search.count() == 53
    assert data_client.count.call_count == 1


def test_count_filter(data_client):
    s = Search(using=data_client).index('git').filter(~Q('exists', field='parent_shas'))
    # initial commit + repo document
    assert 2 == s.count()
