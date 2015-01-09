from elasticsearch_dsl import mapping


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
    m1['author'].property('name', 'string')
    m1.meta('_all', enabled=False)

    m2 = mapping.Mapping('article')
    m2.field('published_from', 'date')
    m2.field('author', 'object')
    m2.field('title', 'string')
    m2.field('lang', 'string', index='not_analyzed')
    m2.meta('_analyzer', path='lang')
    m2['author'].property('email', 'string')

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
