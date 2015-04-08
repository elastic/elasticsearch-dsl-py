from hashlib import md5
from datetime import datetime

from elasticsearch_dsl import document, field, Mapping
from elasticsearch_dsl.exceptions import ValidationException

from pytest import raises

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

def test_meta_field_mapping():
    class User(document.DocType):
        username = field.String()
        class Meta:
            all = document.MetaField(enabled=False)
            _index = document.MetaField(enabled=True)

    assert {
        'user': {
            'properties': {
                'username': {'type': 'string'}
            },
            '_all': {'enabled': False},
            '_index': {'enabled': True},
        }
    } == User._doc_type.mapping.to_dict()

def test_multi_value_fields():
    class Blog(document.DocType):
        tags = field.String(multi=True, index='not_analyzed')

    b = Blog()
    assert [] == b.tags
    b.tags.append('search')
    b.tags.append('python')
    assert ['search', 'python'] == b.tags

def test_docs_with_properties():
    class User(document.DocType):
        pwd_hash = field.String()

        def check_password(self, pwd):
            return md5(pwd).hexdigest() == self.pwd_hash

        @property
        def password(self):
            raise AttributeError('readonly')

        @password.setter
        def password(self, pwd):
            self.pwd_hash = md5(pwd).hexdigest()

    u = User(pwd_hash=md5(b'secret').hexdigest())
    assert u.check_password(b'secret')
    assert not u.check_password(b'not-secret')

    u.password = b'not-secret'
    assert 'password' not in u._d_
    assert not u.check_password(b'secret')
    assert u.check_password(b'not-secret')

    with raises(AttributeError):
        u.password

def test_nested_can_be_assigned_to():
    d1 = DocWithNested(comments=[{'title': 'First!'}])
    d2 = DocWithNested()

    d2.comments = d1.comments
    assert d2.comments == [{'title': 'First!'}]

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

def test_invalid_date_will_raise_exception():
    md = MyDoc()
    with raises(ValidationException):
        md.created_at = None

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
    md = MySubDoc(meta={'id': 42}, name='My First doc!')

    md.meta.index = 'my-index'
    assert md.meta.index == 'my-index'
    assert md.meta.id == 42
    assert {'name': 'My First doc!'} == md.to_dict()
    assert {'id': 42, 'index': 'my-index'} == md.meta.to_dict()

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

def test_meta_fields_can_be_accessed_directly_with_underscore():
    p = object()
    md = MyDoc(_id=42, title='Hello World!')
    md._parent = p

    assert md.meta.id == 42
    assert md._id == 42
    assert md.meta.parent is md._parent is p
