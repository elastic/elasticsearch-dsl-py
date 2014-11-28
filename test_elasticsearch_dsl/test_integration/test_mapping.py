from elasticsearch_dsl import mapping

def test_mapping_gets_updated_from_es(client):
    client.indices.create(
        index='test-mapping',
        body={
            'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
            'mappings': {
                'my_doc': {
                    'properties': {
                        'title': {
                            'type': 'string',
                            'analyzer': 'snowball',
                            'fields': {
                                'raw': {'type': 'string', 'index': 'not_analyzed'}
                            }
                        },
                        'created_at': {'type': 'date'},
                        'comments': {
                            'type': 'nested',
                            'created': {'type': 'date'},
                            'properties': {
                                'author': {
                                    'type': 'string',
                                    'analyzer': 'snowball',
                                    'fields': {
                                        'raw': {'type': 'string', 'index': 'not_analyzed'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    
    m = mapping.Mapping.from_es('test-mapping', 'my_doc', using=client)

    assert ['comments', 'created_at', 'title'] == list(sorted(m.properties.properties._d_.keys()))
    assert {
        'my_doc': {
            'properties': {
                'comments': {
                    'type': 'nested',
                    'properties': {
                        'author': {'analyzer': 'snowball', 'fields': {'raw': {'index': 'not_analyzed', 'type': 'string'}}, 'type': 'string'}
                    },
                },
                'created_at': {'format': 'dateOptionalTime', 'type': 'date'},
                'title': {'analyzer': 'snowball', 'fields': {'raw': {'index': 'not_analyzed', 'type': 'string'}}, 'type': 'string'}
            }
        }
    } == m.to_dict()
