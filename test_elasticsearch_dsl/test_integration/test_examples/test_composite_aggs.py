from elasticsearch_dsl import Search, A

from .composite_agg import scan_aggs

def test_scan_aggs_exhausts_all_files(data_client):
    s = Search(index='flat-git')
    key_aggs = {'files': A('terms', field='files')}
    file_list = list(scan_aggs(s, key_aggs))

    assert len(file_list) == 26

def test_scan_aggs_with_multiple_aggs(data_client):
    s = Search(index='flat-git')
    key_aggs = [
        {'files': A('terms', field='files')},
        {'months': {'date_histogram': {'field': 'committed_date', 'interval': 'month'}}},
    ]
    file_list = list(scan_aggs(s, key_aggs))

    assert len(file_list) == 47
