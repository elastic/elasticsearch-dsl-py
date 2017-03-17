from elasticsearch_dsl import mapping, analysis, exceptions

from pytest import raises

def test_mapping_saved_into_es(write_client):
    m = mapping.Mapping('test-type')
    m.field('name', 'text', analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
    m.field('tags', 'keyword')
    m.save('test-mapping', using=write_client)

    m = mapping.Mapping('other-type')
    m.field('title', 'text').field('categories', 'keyword')

    m.save('test-mapping', using=write_client)


    assert write_client.indices.exists_type(index='test-mapping', doc_type='test-type')
    assert {
        'test-mapping': {
            'mappings': {
                'test-type': {
                    'properties': {
                        'name': {'type': 'text', 'analyzer': 'my_analyzer'},
                        'tags': {'type': 'keyword'}
                    }
                },
                'other-type': {
                    'properties': {
                        'title': {'type': 'text'},
                        'categories': {'type': 'keyword'}
                    }
                }
            }
        }
    } == write_client.indices.get_mapping(index='test-mapping')

def test_mapping_saved_into_es_when_index_already_exists_closed(write_client):
    m = mapping.Mapping('test-type')
    m.field('name', 'text', analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
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
                        'name': {'type': 'text', 'analyzer': 'my_analyzer'},
                    }
                }
            }
        }
    } == write_client.indices.get_mapping(index='test-mapping')

def test_mapping_saved_into_es_when_index_already_exists_with_analysis(write_client):
    m = mapping.Mapping('test-type')
    analyzer = analysis.analyzer('my_analyzer', tokenizer='keyword')
    m.field('name', 'text', analyzer=analyzer)

    new_analysis = analyzer.get_analysis_definition()
    new_analysis['analyzer']['other_analyzer'] = {
        'type': 'custom',
        'tokenizer': 'whitespace'
    }
    write_client.indices.create(index='test-mapping', body={'settings': {'analysis': new_analysis}})

    m.field('title', 'text', analyzer=analyzer)
    m.save('test-mapping', using=write_client)

    assert {
        'test-mapping': {
            'mappings': {
                'test-type': {
                    'properties': {
                        'name': {'type': 'text', 'analyzer': 'my_analyzer'},
                        'title': {'type': 'text', 'analyzer': 'my_analyzer'},
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
                            'type': 'text',
                            'analyzer': 'snowball',
                            'fields': {
                                'raw': {'type': 'keyword'}
                            }
                        },
                        'created_at': {'type': 'date'},
                        'comments': {
                            'type': 'nested',
                            'properties': {
                                'created': {'type': 'date'},
                                'author': {
                                    'type': 'text',
                                    'analyzer': 'snowball',
                                    'fields': {
                                        'raw': {'type': 'keyword'}
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
                        'created': {'type': 'date'},
                        'author': {'analyzer': 'snowball', 'fields': {'raw': {'type': 'keyword'}}, 'type': 'text'}
                    },
                },
                'created_at': {'type': 'date'},
                'title': {'analyzer': 'snowball', 'fields': {'raw': {'type': 'keyword'}}, 'type': 'text'}
            }
        }
    } == m.to_dict()

    # test same with alias
    write_client.indices.put_alias(index='test-mapping', name='test-alias')

    m2 = mapping.Mapping.from_es('test-alias', 'my_doc', using=write_client)
    assert m2.to_dict() == m.to_dict()
