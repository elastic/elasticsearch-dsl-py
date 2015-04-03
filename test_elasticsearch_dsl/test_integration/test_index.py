from elasticsearch_dsl import DocType, Index, String, Date, analysis

class Post(DocType):
    title = String(analyzer=analysis.analyzer('my_analyzer', tokenizer='keyword'))
    published_from = Date()

class User(DocType):
    username = String(index='not_analyzed')
    joined_date = Date()

def test_index_can_be_created_with_settings_and_mappings(write_client):
    i = Index('test-blog', using=write_client)
    i.doc_type(Post)
    i.doc_type(User)
    i.settings(number_of_replicas=0, number_of_shards=1)
    i.create()

    assert {
        'test-blog': {
            'mappings': {
                'post': {
                    'properties': {
                        'title': {'type': 'string', 'analyzer': 'my_analyzer'},
                        'published_from': {'type': 'date', 'format': 'dateOptionalTime',},
                    }
                },
                'user': {
                    'properties': {
                        'username': {'type': 'string', 'index': 'not_analyzed'},
                        'joined_date': {'type': 'date', 'format': 'dateOptionalTime',},
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
