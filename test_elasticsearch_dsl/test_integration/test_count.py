from elasticsearch_dsl.search import Search, Q

def test_count_all(data_client):
    s = Search(using=data_client).index('git')
    assert 53 == s.count()

def test_count_type(data_client):
    s = Search(using=data_client).index('git').doc_type('repos')
    assert 1 == s.count()

def test_count_filter(data_client):
    s = Search(using=data_client).index('git').filter(~Q('exists', field='parent_shas'))
    # initial commit + repo document
    assert 2 == s.count()
