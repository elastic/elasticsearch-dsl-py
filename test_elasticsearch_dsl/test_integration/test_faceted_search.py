from datetime import datetime

from elasticsearch_dsl.faceted_search import FacetedSearch, TermsFacet, DateHistogramFacet, RangeFacet

class CommitSearch(FacetedSearch):
    doc_types = ['commits']
    fields = ('description', 'files', )

    facets = {
        'files': TermsFacet(field='files'),
        'frequency': DateHistogramFacet(field='authored_date', interval="day", min_doc_count=1),
        'deletions': RangeFacet(field='stats.deletions', ranges=[('ok', (None, 1)), ('good', (1, 5)), ('better', (5, None))])
    }


def test_empty_search_finds_everything(data_client):
    cs = CommitSearch()

    r = cs.execute()

    assert r.hits.total == 52
    assert [
        ('elasticsearch_dsl', 40, False),
        ('test_elasticsearch_dsl', 35, False),
        ('elasticsearch_dsl/query.py', 19, False),
        ('test_elasticsearch_dsl/test_search.py', 15, False),
        ('elasticsearch_dsl/utils.py', 14, False),
        ('test_elasticsearch_dsl/test_query.py', 13, False),
        ('elasticsearch_dsl/search.py', 12, False),
        ('elasticsearch_dsl/aggs.py', 11, False),
        ('test_elasticsearch_dsl/test_result.py', 5, False),
        ('elasticsearch_dsl/result.py', 3, False)
    ] == r.facets.files

    assert [
        (datetime(2014, 3, 3, 0, 0), 2, False),
        (datetime(2014, 3, 4, 0, 0), 1, False),
        (datetime(2014, 3, 5, 0, 0), 3, False),
        (datetime(2014, 3, 6, 0, 0), 3, False),
        (datetime(2014, 3, 7, 0, 0), 9, False),
        (datetime(2014, 3, 10, 0, 0), 2, False),
        (datetime(2014, 3, 15, 0, 0), 4, False),
        (datetime(2014, 3, 21, 0, 0), 2, False),
        (datetime(2014, 3, 23, 0, 0), 2, False),
        (datetime(2014, 3, 24, 0, 0), 10, False),
        (datetime(2014, 4, 20, 0, 0), 2, False),
        (datetime(2014, 4, 22, 0, 0), 2, False),
        (datetime(2014, 4, 25, 0, 0), 3, False),
        (datetime(2014, 4, 26, 0, 0), 2, False),
        (datetime(2014, 4, 27, 0, 0), 2, False),
        (datetime(2014, 5, 1, 0, 0), 2, False),
        (datetime(2014, 5, 2, 0, 0), 1, False)
     ] == r.facets.frequency

    assert [
        ('ok', 19, False),
        ('good', 14, False),
        ('better', 19, False)
    ] == r.facets.deletions

def test_term_filters_are_shown_as_selected_and_data_is_filtered(data_client):
    cs = CommitSearch(filters={'files': 'test_elasticsearch_dsl'})

    r = cs.execute()

    assert 35 == r.hits.total
    assert [
        ('elasticsearch_dsl', 40, False),
        ('test_elasticsearch_dsl', 35, True), # selected
        ('elasticsearch_dsl/query.py', 19, False),
        ('test_elasticsearch_dsl/test_search.py', 15, False),
        ('elasticsearch_dsl/utils.py', 14, False),
        ('test_elasticsearch_dsl/test_query.py', 13, False),
        ('elasticsearch_dsl/search.py', 12, False),
        ('elasticsearch_dsl/aggs.py', 11, False),
        ('test_elasticsearch_dsl/test_result.py', 5, False),
        ('elasticsearch_dsl/result.py', 3, False)
    ] == r.facets.files

    assert [
        (datetime(2014, 3, 3, 0, 0), 1, False),
        (datetime(2014, 3, 5, 0, 0), 2, False),
        (datetime(2014, 3, 6, 0, 0), 3, False),
        (datetime(2014, 3, 7, 0, 0), 6, False),
        (datetime(2014, 3, 10, 0, 0), 1, False),
        (datetime(2014, 3, 15, 0, 0), 3, False),
        (datetime(2014, 3, 21, 0, 0), 2, False),
        (datetime(2014, 3, 23, 0, 0), 1, False),
        (datetime(2014, 3, 24, 0, 0), 7, False),
        (datetime(2014, 4, 20, 0, 0), 1, False),
        (datetime(2014, 4, 25, 0, 0), 3, False),
        (datetime(2014, 4, 26, 0, 0), 2, False),
        (datetime(2014, 4, 27, 0, 0), 1, False),
        (datetime(2014, 5, 1, 0, 0), 1, False),
        (datetime(2014, 5, 2, 0, 0), 1, False)
    ] == r.facets.frequency

    assert [
        ('ok', 12, False),
        ('good', 10, False),
        ('better', 13, False)
    ] == r.facets.deletions

def test_range_filters_are_shown_as_selected_and_data_is_filtered(data_client):
    cs = CommitSearch(filters={'deletions': 'better'})

    r = cs.execute()

    assert 19 == r.hits.total

def test_pagination(data_client):
    cs = CommitSearch()
    cs = cs[0:20]

    assert 52 == cs.count()
    assert 20 == len(cs.execute())
