from elasticsearch_dsl import document, field

def test_declarative_mapping_definition():
    class MyDoc(document.DocType):
        title = field.String(index='not_analyzed')
        name = field.String()
        created_at = field.Date()

    assert hasattr(MyDoc, '_mapping_')
    assert {
        'MyDoc': {
            'properties': {
                'created_at': {'type': 'date'},
                'name': {'type': 'string'},
                'title': {'index': 'not_analyzed', 'type': 'string'}
            }
        }
    } == MyDoc._mapping_.to_dict()
