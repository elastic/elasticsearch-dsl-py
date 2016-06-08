from elasticsearch_dsl.faceted_search import FacetedSearch, TermsFacet

class BlogSearch(FacetedSearch):
    doc_types = ['user', 'post']
    fields = ('title^5', 'body', )

    facets = {
        'category': TermsFacet(field='category.raw'),
        'tags': TermsFacet(field='tags'),
    }


def test_query_is_created_properly():
    bs = BlogSearch('python search')
    s = bs.build_search()

    assert s._doc_type == ['user', 'post']
    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {
                    'match_all': {},
                },
                'aggs': {'tags': {'terms': {'field': 'tags'}}},
            },
            '_filter_category': {
                'filter': {
                    'match_all': {},
                },
                'aggs': {'category': {'terms': {'field': 'category.raw'}}},
            },
        },
        'query': {
            'multi_match': {'fields': ('title^5', 'body'), 'query': 'python search'}
        },
        'highlight': {'fields': {'body': {}, 'title': {}}}
    } == s.to_dict()

def test_filter_is_applied_to_search_but_not_relevant_facet():
    bs = BlogSearch('python search', filters={'category': 'elastic'})
    s = bs.build_search()

    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {'terms': {'category.raw': ['elastic']}},
                'aggs': {'tags': {'terms': {'field': 'tags'}}},
            },
            '_filter_category': {
                'filter': {
                    'match_all': {},
                },
                'aggs': {'category': {'terms': {'field': 'category.raw'}}},
            }
        },
        'post_filter': {'terms': {'category.raw': ['elastic']}},
        'query': {
            'multi_match': {'fields': ('title^5', 'body'), 'query': 'python search'}
        },
        'highlight': {'fields': {'body': {}, 'title': {}}}
    } == s.to_dict()

def test_filters_are_applied_to_search_ant_relevant_facets():
    bs = BlogSearch('python search', filters={'category': 'elastic', 'tags': ['python', 'django']})
    s = bs.build_search()

    d = s.to_dict()


    # we need to test post_filter without relying on order
    f = d['post_filter']['bool'].pop('must')
    assert len(f) == 2
    assert {'terms': {'category.raw': ['elastic']}} in f
    assert {'terms': {'tags': ['python', 'django']}} in f

    assert {
        'aggs': {
            '_filter_tags': {
                'filter': {
                    'terms': {'category.raw': ['elastic']},
                },
                'aggs': {'tags': {'terms': {'field': 'tags'}}},
            },
            '_filter_category': {
                'filter': {
                    'terms': {'tags': ['python', 'django']},
                },
                'aggs': {'category': {'terms': {'field': 'category.raw'}}},
            }
        },
        'query': {
            'multi_match': {'fields': ('title^5', 'body'), 'query': 'python search'}
        },
        'post_filter': {
            'bool': {
            }
        },
        'highlight': {'fields': {'body': {}, 'title': {}}}
    } == d

