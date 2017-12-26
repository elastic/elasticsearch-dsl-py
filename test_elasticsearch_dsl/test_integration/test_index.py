from elasticsearch_dsl import DocType, Index, Text, Keyword, Date, analysis, IndexTemplate

class Post(DocType):
    title = Text(analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
    published_from = Date()

def test_index_template_works(write_client):
    it = IndexTemplate('test-template', 'test-*')
    it.doc_type(Post)
    it.settings(number_of_replicas=0, number_of_shards=1)
    it.save()

    i = Index('test-blog')
    i.create()

    assert {
        'test-blog': {
            'mappings': {
                'doc': {
                    'properties': {
                        'title': {'type': 'text', 'analyzer': 'my_analyzer'},
                        'published_from': {'type': 'date'},
                    }
                },
            }
        }
    } == write_client.indices.get_mapping(index='test-blog')


def test_index_exists(data_client):
    assert Index('git').exists()
    assert not Index('not-there').exists()

def test_index_can_be_created_with_settings_and_mappings(write_client):
    i = Index('test-blog', using=write_client)
    i.doc_type(Post)
    i.settings(number_of_replicas=0, number_of_shards=1)
    i.create()

    assert {
        'test-blog': {
            'mappings': {
                'doc': {
                    'properties': {
                        'title': {'type': 'text', 'analyzer': 'my_analyzer'},
                        'published_from': {'type': 'date'}
                    }
                },
            }
        }
    } == write_client.indices.get_mapping(index='test-blog')

    settings = write_client.indices.get_settings(index='test-blog')
    assert settings['test-blog']['settings']['index']['number_of_replicas'] == '0'
    assert settings['test-blog']['settings']['index']['number_of_shards'] == '1'
    assert settings['test-blog']['settings']['index']['analysis'] == {
        'analyzer': {
            'my_analyzer': {
                'type': 'custom',
                'tokenizer': 'keyword'
            }
        }
    }

def test_delete(write_client):
    write_client.indices.create(
        index='test-index',
        body={'settings': {'number_of_replicas': 0, 'number_of_shards': 1}}
    )

    i = Index('test-index', using=write_client)
    i.delete()
    assert not write_client.indices.exists(index='test-index')

def test_multiple_indices_with_same_doc_type_work(write_client):
    i1 = Index('test-index-1', using=write_client)
    i2 = Index('test-index-2', using=write_client)

    for i in (i1, i2):
        i.doc_type(Post)
        i.create()

    for i in ('test-index-1', 'test-index-2'):
        settings = write_client.indices.get_settings(index=i)
        assert settings[i]['settings']['index']['analysis'] == {
            'analyzer': {
                'my_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'keyword'
                }
            }
        }
