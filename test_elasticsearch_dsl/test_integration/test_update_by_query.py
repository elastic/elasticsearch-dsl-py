from elasticsearch_dsl.update_by_query import UpdateByQuery
from elasticsearch_dsl.search import Q
from elasticsearch.helpers import bulk

def test_update_by_query_no_script(write_client, setup_ubq_tests):
    index = setup_ubq_tests

    ubq = UpdateByQuery(using=write_client).index(index).filter(~Q('exists', field='is_public'))
    response = ubq.execute()

    assert response.total == 52
    assert response['took'] > 0
    assert not response.timed_out
    assert response.updated == 52
    assert response.deleted == 0
    assert response.took > 0

def test_update_by_query_with_script(write_client, setup_ubq_tests):
    index = setup_ubq_tests

    ubq = UpdateByQuery(using=write_client).index(index)\
        .filter(~Q('exists', field='parent_shas'))\
        .script(source='ctx._source.is_public = false')
    ubq = ubq.params(conflicts='proceed')

    response = ubq.execute()
    assert response.total == 2
    assert response.updated == 2
    assert response.version_conflicts == 0

def test_delete_by_query_with_script(write_client, setup_ubq_tests):
    index = setup_ubq_tests

    ubq = UpdateByQuery(using=write_client).index(index)\
        .filter(Q('match', parent_shas='1dd19210b5be92b960f7db6f66ae526288edccc3'))\
        .script(source='ctx.op = "delete"')
    ubq = ubq.params(conflicts='proceed')

    response = ubq.execute()

    assert response.total == 1
    assert response.deleted == 1
