from elasticsearch_dsl import mapping, analysis, exceptions

from pytest import raises

def test_mapping_saved_into_es(write_client):
    m = mapping.Mapping('test-type')
    m.field('name', 'string', analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
    m.field('tags', 'string', index='not_analyzed')
    m.save('test-mapping', using=write_client)

    m = mapping.Mapping('other-type')
    m.field('title', 'string').field('categories', 'string', index='not_analyzed')

    m.save('test-mapping', using=write_client)


    assert write_client.indices.exists_type(index='test-mapping', doc_type='test-type')
    assert {
        'test-mapping': {
            'mappings': {
                'test-type': {
                    'properties': {
                        'name': {'type': 'string', 'analyzer': 'my_analyzer'},
                        'tags': {'index': 'not_analyzed', 'type': 'string'}
                    }
                },
                'other-type': {
                    'properties': {
                        'title': {'type': 'string'},
                        'categories': {'index': 'not_analyzed', 'type': 'string'}
                    }
                }
            }
        }
    } == write_client.indices.get_mapping(index='test-mapping')

def test_mapping_saved_into_es_when_index_already_exists_closed(write_client):
    m = mapping.Mapping('test-type')
    m.field('name', 'string', analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
    write_client.indices.create(index='test-mapping')

    with raises(exceptions.IllegalOperation):
        m.save('test-mapping', using=write_client)

    write_client.cluster.health(index='test-mapping', wait_for_status='yellow')
    write_client.indices.close(index='test-mapping')
    m.save('test-mapping', using=write_client)


    assert {
        'test-mapping': {
            'mappings': {
                'test-type': {
                    'properties': {
                        'name': {'type': 'string', 'analyzer': 'my_analyzer'},
                    }
                }
            }
        }
    } == write_client.indices.get_mapping(index='test-mapping')

def test_mapping_gets_updated_from_es(write_client):
    write_client.indices.create(
        index='test-mapping',
        body={
            'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
            'mappings': {
                'my_doc': {
                    'date_detection': False,
                    '_all': {'enabled': False},
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
                            'properties': {
                                'created': {'type': 'date'},
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
    
    m = mapping.Mapping.from_es('test-mapping', 'my_doc', using=write_client)

    assert ['comments', 'created_at', 'title'] == list(sorted(m.properties.properties._d_.keys()))
    assert {
        'my_doc': {
            'date_detection': False,
            '_all': {'enabled': False},
            'properties': {
                'comments': {
                    'type': 'nested',
                    'properties': {
                        'created': {'type': 'date', 'format': 'strict_date_optional_time||epoch_millis'},
                        'author': {'analyzer': 'snowball', 'fields': {'raw': {'index': 'not_analyzed', 'type': 'string'}}, 'type': 'string'}
                    },
                },
                'created_at': {'format': 'strict_date_optional_time||epoch_millis', 'type': 'date'},
                'title': {'analyzer': 'snowball', 'fields': {'raw': {'index': 'not_analyzed', 'type': 'string'}}, 'type': 'string'}
            }
        }
    } == m.to_dict()

    # test same with alias
    write_client.indices.put_alias(index='test-mapping', name='test-alias')

    m2 = mapping.Mapping.from_es('test-alias', 'my_doc', using=write_client)
    assert m2.to_dict() == m.to_dict()
