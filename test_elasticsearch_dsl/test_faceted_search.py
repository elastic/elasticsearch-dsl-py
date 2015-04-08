from datetime import datetime
from elasticsearch_dsl.faceted_search import FacetedSearch, agg_to_filter
from elasticsearch_dsl import A, F

class BlogSearch(FacetedSearch):
    doc_types = ['user', 'post']
    fields = ('title', 'body', )

    facets = {
        'category': A('terms', field='category.raw'),
        'tags': A('terms', field='tags'),
    }


def test_agg_filter_for_date_histograms():
    a = A('date_histogram', field='published_date', interval='month')
    f = agg_to_filter(a, datetime(2014, 12, 1))

    assert f == F('range', published_date={'gte': datetime(2014, 12, 1), 'lt': datetime(2015, 1, 1)})

def test_query_is_created_properly():
    bs = BlogSearch('python search')
    s = bs.build_search()

    assert s._doc_type == ['user', 'post']
    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {
                    'match_all': {},
                    'aggs': {'tags': {'terms': {'field': 'tags'}}},
                }
            },
            '_filter_category': {
                'filter': {
                    'match_all': {},
                    'aggs': {'category': {'terms': {'field': 'category.raw'}}},
                }
            },
        },
        'query': {
            'multi_match': {'fields': ('title', 'body'), 'query': 'python search'}
        }
    } == s.to_dict()

def test_filter_is_applied_to_search_but_not_relevant_facet():
    bs = BlogSearch('python search', filters={'category': 'elastic'})
    s = bs.build_search()

    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {
                    'term': {'category.raw': 'elastic'},
                    'aggs': {'tags': {'terms': {'field': 'tags'}}},
                }
            },
            '_filter_category': {
                'filter': {
                    'match_all': {},
                    'aggs': {'category': {'terms': {'field': 'category.raw'}}},
                }
            }
        },
        'post_filter': {
            'term': {'category.raw': 'elastic'}
        },
        'query': {
            'multi_match': {'fields': ('title', 'body'), 'query': 'python search'}
        }
    } == s.to_dict()

def test_filters_are_applied_to_search_ant_relevant_facets():
    bs = BlogSearch('python search', filters={'category': 'elastic', 'tags': 'python'})
    s = bs.build_search()

    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {
                    'term': {'category.raw': 'elastic'},
                    'aggs': {'tags': {'terms': {'field': 'tags'}}},
                }
            },
            '_filter_category': {
                'filter': {
                    'term': {'tags': 'python'},
                    'aggs': {'category': {'terms': {'field': 'category.raw'}}},
                }
            }
        },
        'post_filter': {
            'bool': {
                'must': [
                    {'term': {'tags': 'python'}},
                    {'term': {'category.raw': 'elastic'}},
                ]
            }
        },
        'query': {
            'multi_match': {'fields': ('title', 'body'), 'query': 'python search'}
        }
    } == s.to_dict()

