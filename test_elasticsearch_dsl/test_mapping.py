import json

from elasticsearch_dsl import mapping, String, Nested, analysis


def test_mapping_can_has_fields():
    m = mapping.Mapping('article')
    m.field('name', 'string').field('tags', 'string', index='not_analyzed')

    assert {
        'article': {
            'properties': {
                'name': {'type': 'string'},
                'tags': {'index': 'not_analyzed', 'type': 'string'}
            }
        }
    } == m.to_dict()

def test_mapping_update_is_recursive():
    m1 = mapping.Mapping('article')
    m1.field('title', 'string')
    m1.field('author', 'object')
    m1['author'].field('name', 'string')
    m1.meta('_all', enabled=False)
    m1.meta('dynamic', False)

    m2 = mapping.Mapping('article')
    m2.field('published_from', 'date')
    m2.field('author', 'object')
    m2.field('title', 'string')
    m2.field('lang', 'string', index='not_analyzed')
    m2.meta('_analyzer', path='lang')
    m2['author'].field('email', 'string')

    m1.update(m2, update_only=True)

    assert {
        'article': {
            '_all': {'enabled': False},
            '_analyzer': {'path': 'lang'},
            'dynamic': False,
            'properties': {
                'published_from': {'type': 'date'},
                'title': {'type': 'string'},
                'lang': {'type': 'string', 'index': 'not_analyzed'},
                'author': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                    }
                }
            }
        }
    } == m1.to_dict()

def test_properties_can_iterate_over_all_the_fields():
    m = mapping.Mapping('testing')
    m.field('f1', 'string', test_attr='f1', fields={'f2': String(test_attr='f2')})
    m.field('f3', Nested(test_attr='f3', properties={
            'f4': String(test_attr='f4')}))

    assert set(('f1', 'f2', 'f3', 'f4')) == set(f.test_attr for f in m.properties._collect_fields())

def test_mapping_can_collect_all_analyzers():
    a1 = analysis.analyzer('my_analyzer1',
        tokenizer='keyword',
        filter=['lowercase', analysis.token_filter('my_filter1', 'stop', stopwords=['a', 'b'])],
    )
    a2 = analysis.analyzer('english')
    a3 = analysis.analyzer('unknown_custom')
    a4 = analysis.analyzer('my_analyzer2',
        tokenizer=analysis.tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
        filter=[analysis.token_filter('my_filter2', 'stop', stopwords=['c', 'd'])],
    )
    a5 = analysis.analyzer('my_analyzer3', tokenizer='keyword')

    m = mapping.Mapping('article')
    m.field('title', 'string', analyzer=a1,
        fields={
            'english': String(index_analyzer=a2),
            'unknown': String(search_analyzer=a3),
        }
    )
    m.field('comments', Nested(properties={
        'author': String(index_analyzer=a4)
    }))
    m.meta('_all', analyzer=a5)

    assert {
        'analyzer': {
            'my_analyzer1': {'filter': ['lowercase', 'my_filter1'], 'tokenizer': 'keyword', 'type': 'custom'},
            'my_analyzer2': {'filter': ['my_filter2'], 'tokenizer': 'trigram', 'type': 'custom'},
            'my_analyzer3': {'tokenizer': 'keyword', 'type': 'custom'},
        },
        'filter': {
            'my_filter1': {'stopwords': ['a', 'b'], 'type': 'stop'},
            'my_filter2': {'stopwords': ['c', 'd'], 'type': 'stop'},
        },
        'tokenizer': {
            'trigram': {'max_gram': 3, 'min_gram': 3, 'type': 'nGram'},
        }
    } == m._collect_analysis()

    assert json.loads(json.dumps(m.to_dict())) == m.to_dict()


def test_mapping_can_collect_multiple_analyzers():
    a1 = analysis.analyzer(
        'my_analyzer1',
        tokenizer='keyword',
        filter=['lowercase', analysis.token_filter('my_filter1', 'stop', stopwords=['a', 'b'])],
    )
    a2 = analysis.analyzer(
        'my_analyzer2',
        tokenizer=analysis.tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
        filter=[analysis.token_filter('my_filter2', 'stop', stopwords=['c', 'd'])],
    )
    m = mapping.Mapping('article')
    m.field('title', 'string', analyzer=a1, index_analyzer=a1, search_analyzer=a2)
    m.field(
        'text', 'string', analyzer=a1,
        fields={
            'english': String(index_analyzer=a1),
            'unknown': String(index_analyzer=a1, search_analyzer=a2),
        }
    )
    assert {
       'analyzer': {
           'my_analyzer1': {'filter': ['lowercase', 'my_filter1'],
                            'tokenizer': 'keyword',
                            'type': 'custom'},
           'my_analyzer2': {'filter': ['my_filter2'],
                            'tokenizer': 'trigram',
                            'type': 'custom'}},
       'filter': {
           'my_filter1': {'stopwords': ['a', 'b'], 'type': 'stop'},
           'my_filter2': {'stopwords': ['c', 'd'], 'type': 'stop'}},
       'tokenizer': {'trigram': {'max_gram': 3, 'min_gram': 3, 'type': 'nGram'}}
    } == m._collect_analysis()

def test_even_non_custom_analyzers_can_have_params():
    a1 = analysis.analyzer('whitespace', type='pattern', pattern=r'\\s+')
    m = mapping.Mapping('some_type')
    m.field('title', 'string', analyzer=a1)

    assert {
        "analyzer": {
            "whitespace": {
                "type": "pattern",
                "pattern": r"\\s+"
            }
            }
    } == m._collect_analysis()
