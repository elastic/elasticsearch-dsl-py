from elasticsearch_dsl import mapping, String, Nested, Date


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
