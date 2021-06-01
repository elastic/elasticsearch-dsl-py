from elasticsearch2_dsl.search import Search

def test_count_all(data_client):
    s = Search(using=data_client).index('git')
    assert 53 == s.count()

def test_count_type(data_client):
    s = Search(using=data_client).index('git').doc_type('repos')
    assert 1 == s.count()

def test_count_filter(data_client):
    s = Search(using=data_client).index('git').filter('missing', field='parent_shas')
    # initial commit + repo document
    assert 2 == s.count()

def test_search_type_count(data_client):
    s = Search(using=data_client, index='git')
    s.aggs.bucket('per_type', 'terms', field='_type')
    s = s.params(search_type='count')
    result = s.execute()

    assert [] == result.hits
    assert 2 == len(result.aggregations.per_type.buckets)
