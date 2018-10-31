from elasticsearch_dsl.update_by_query import UpdateByQuery
from elasticsearch_dsl.search import Q

def test_update_by_query_no_script(data_client):
    ubq = UpdateByQuery(using=data_client).index('git').filter(~Q('exists', field='is_public'))
    response = ubq.execute()

    assert response.total == 52
    assert response['took'] > 0
    assert not response.timed_out
    assert response.updated == 52
    assert response.deleted == 0
    assert response.took > 0

def test_update_by_query_with_script(data_client):
    ubq = UpdateByQuery(using=data_client).index('git')\
        .filter(~Q('exists', field='parent_shas'))\
        .script(source='ctx._source.is_public = false')
    ubq = ubq.params(conflicts='proceed')

    response = ubq.execute()
    assert response.total == 2
    assert response.updated == 1
    assert response.version_conflicts == 1

def test_delete_by_query_with_script(data_client):
    ubq = UpdateByQuery(using=data_client).index('flat-git')\
        .filter(Q('match', parent_shas='1dd19210b5be92b960f7db6f66ae526288edccc3'))\
        .script(source='ctx.op = "delete"')
    ubq = ubq.params(conflicts='proceed')

    response = ubq.execute()

    assert response.total == 1
    assert response.deleted == 1
