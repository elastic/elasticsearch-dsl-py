from elasticsearch2_dsl.search import Search

def test_search_can_be_limited_to_fields(data_client):
    s = Search(using=data_client).index('git').doc_type('repos').fields('organization')
    response = s.execute()

    assert response.hits.total == 1
    assert response.hits[0] == {'organization': ['elasticsearch']}
