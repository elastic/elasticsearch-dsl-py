from datetime import datetime

from elasticsearch_dsl import document, field

class MyDoc(document.DocType):
    title = field.String(index='not_analyzed')
    name = field.String()
    created_at = field.Date()
    inner = field.Object(properties={'old_field': field.String()})

class MySubDoc(MyDoc):
    name = field.String(index='not_analyzed')

    class Meta:
        doc_type = 'my_custom_doc'
        index = 'default-index'

class MySubSubDoc(MySubDoc):
    extra = field.Long()


def test_to_dict_is_recursive_and_can_cope_with_multi_values():
    md = MyDoc(name=['a', 'b', 'c'])
    md.inner = [{'old_field': 'of1'}, {'old_field': 'of2'}]

    assert {
        'name': ['a', 'b', 'c'],
        'inner': [{'old_field': 'of1'}, {'old_field': 'of2'}],
    } == md.to_dict()

def test_declarative_mapping_definition():
    assert issubclass(MyDoc, document.DocType)
    assert hasattr(MyDoc, '_doc_type')
    assert 'my_doc' == MyDoc._doc_type.name
    assert {
        'my_doc': {
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
    } == MyDoc._doc_type.mapping.to_dict()

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

def test_document_inheritance():
    assert issubclass(MySubDoc, MyDoc)
    assert issubclass(MySubDoc, document.DocType)
    assert hasattr(MySubDoc, '_doc_type')
    assert 'my_custom_doc' == MySubDoc._doc_type.name
    assert {
        'my_custom_doc': {
            'properties': {
                'created_at': {'type': 'date'},
                'name': {'type': 'string', 'index': 'not_analyzed'},
                'title': {'index': 'not_analyzed', 'type': 'string'},
                'inner': {
                    'type': 'object',
                    'properties': {'old_field': {'type': 'string'}}
                }
            }
        }
    } == MySubDoc._doc_type.mapping.to_dict()

def test_meta_fields_are_stored_in_meta_and_ignored_by_to_dict():
    md = MySubDoc(_id=42, name='My First doc!')

    assert md.id == 42
    assert md.index == 'default-index'
    md.index = 'my-index'
    assert md.index == 'my-index'
    assert md._meta.id == 42
    assert {'name': 'My First doc!'} == md.to_dict()
    assert {'id': 42, 'index': 'my-index'} == md._meta.to_dict()

def test_meta_inheritance():
    assert issubclass(MySubSubDoc, MySubDoc)
    assert issubclass(MySubSubDoc, document.DocType)
    assert hasattr(MySubSubDoc, '_doc_type')
    # doc_type should not be inherited
    assert 'my_sub_sub_doc' == MySubSubDoc._doc_type.name
    # index and using should be
    assert MySubSubDoc._doc_type.index == MySubDoc._doc_type.index
    assert MySubSubDoc._doc_type.using == MySubDoc._doc_type.using
    assert {
        'my_sub_sub_doc': {
            'properties': {
                'created_at': {'type': 'date'},
                'name': {'type': 'string', 'index': 'not_analyzed'},
                'title': {'index': 'not_analyzed', 'type': 'string'},
                'inner': {
                    'type': 'object',
                    'properties': {'old_field': {'type': 'string'}}
                },
                'extra': {'type': 'long'}
            }
        }
    } == MySubSubDoc._doc_type.mapping.to_dict()
