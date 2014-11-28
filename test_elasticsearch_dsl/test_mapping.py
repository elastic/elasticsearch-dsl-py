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
