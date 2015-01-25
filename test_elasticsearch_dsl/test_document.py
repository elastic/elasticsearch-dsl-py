from datetime import datetime

from elasticsearch_dsl import document, field, Mapping

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

class MyDoc2(document.DocType):
    extra = field.Long()

class MyMultiSubDoc(MyDoc2, MySubDoc):
    pass

class DocWithNested(document.DocType):
    comments = field.Nested(properties={'title': field.String()})

def test_nested_defaults_to_list_and_can_be_updated():
    md = DocWithNested()

    assert [] == md.comments

    md.comments.append({'title': 'hello World!'})
    assert {'comments': [{'title': 'hello World!'}]} == md.to_dict()

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

def test_you_can_supply_own_mapping_instance():
    class MyD(document.DocType):
        title = field.String()

        class Meta:
            mapping = Mapping('my_d')
            mapping.meta('_all', enabled=False)

    assert {
        'my_d': {
            '_all': {'enabled': False},
            'properties': {'title': {'type': 'string'}}
        }
    } == MyD._doc_type.mapping.to_dict()

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
    md = MySubDoc(id=42, name='My First doc!')

    md._meta.index = 'my-index'
    assert md._meta.index == 'my-index'
    assert md.id == 42
    assert {'name': 'My First doc!'} == md.to_dict()
    assert {'id': 42, 'index': 'my-index'} == md._meta.to_dict()

def test_meta_inheritance():
    assert issubclass(MyMultiSubDoc, MySubDoc)
    assert issubclass(MyMultiSubDoc, MyDoc2)
    assert issubclass(MyMultiSubDoc, document.DocType)
    assert hasattr(MyMultiSubDoc, '_doc_type')
    # doc_type should not be inherited
    assert 'my_multi_sub_doc' == MyMultiSubDoc._doc_type.name
    # index and using should be
    assert MyMultiSubDoc._doc_type.index == MySubDoc._doc_type.index
    assert MyMultiSubDoc._doc_type.using == MySubDoc._doc_type.using
    assert {
        'my_multi_sub_doc': {
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
    } == MyMultiSubDoc._doc_type.mapping.to_dict()
