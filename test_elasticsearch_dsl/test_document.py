from datetime import datetime

from elasticsearch_dsl import document, field, utils

class MyDoc(document.DocType):
    title = field.String(index='not_analyzed')
    name = field.String()
    created_at = field.Date()
    inner = field.Object(properties={'old_field': field.String()})


def test_declarative_mapping_definition():
    assert hasattr(MyDoc, '_mapping_')
    assert {
        'MyDoc': {
            'properties': {
                'created_at': {'type': 'date'},
                'name': {'type': 'string'},
                'title': {'index': 'not_analyzed', 'type': 'string'},
                'inner': {
                    'type': 'object',
                    'properties': {'old_field': {'type': 'string'}}
                }
            }
        }
    } == MyDoc._mapping_.to_dict()

def test_document_can_be_created_dynamicaly():
    n = datetime.now()
    md = MyDoc(title='hello')
    md.name = 'My Fancy Document!'
    md.created_at = n

    inner = md.inner
    # consistent returns
    assert inner is md.inner
    inner.old_field = 'Already defined.'

    md.inner.new_field = ['undefined', 'field']

    assert {
        'title': 'hello',
        'name': 'My Fancy Document!',
        'created_at': n,
        'inner': {
            'old_field': 'Already defined.',
            'new_field': ['undefined', 'field']
        }
    } == md.to_dict()
