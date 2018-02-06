from elasticsearch_dsl import DocType, Index, Text, Date, analyzer, Mapping, \
    exceptions

from random import choice
import string

from pytest import raises

class Post(DocType):
    title = Text()
    published_from = Date()

def test_doc_type_can_be_set():
    i = Index('i', doc_type='t')
    m = Mapping('t')
    m.field('title', Text())
    i.mapping(m)

    assert {
        'mappings': {
            't': {
                'properties': {
                    'title': {'type': 'text'}
                }
            }
        }
    } == i.to_dict()

def test_conflicting_doc_types_cause_exception():
    i = Index('i', doc_type='t')

    with raises(exceptions.IllegalOperation):
        i.doc_type(Post)

def test_multiple_doc_types_will_combine_mappings():
    class User(DocType):
        username = Text()

    i = Index('i')
    i.doc_type(Post)
    i.doc_type(User)
    assert {
        'mappings': {
            'doc': {
                'properties': {
                    'title': {'type': 'text'},
                    'username': {'type': 'text'},
                    'published_from': {'type': 'date'}
                }
            }
        }
    } == i.to_dict()

def test_search_is_limited_to_index_name():
    i = Index('my-index')
    s = i.search()

    assert s._index == ['my-index']

def test_cloned_index_has_copied_settings_and_using():
    client = object()
    i = Index('my-index', using=client)
    i.settings(number_of_shards=1)

    i2 = i.clone('my-other-index')

    assert 'my-other-index' == i2._name
    assert client is i2._using
    assert i._settings == i2._settings
    assert i._settings is not i2._settings

def test_cloned_index_has_analysis_attribute():
    """
    Regression test for Issue #582 in which `Index.clone()` was not copying
    over the `_analysis` attribute.
    """
    client = object()
    i = Index('my-index', using=client)

    random_analyzer_name = ''.join((choice(string.ascii_letters) for _ in range(100)))
    random_analyzer = analyzer(random_analyzer_name, tokenizer="standard", filter="standard")

    i.analyzer(random_analyzer)

    i2 = i.clone('my-clone-index')

    assert i.to_dict()['settings']['analysis'] == i2.to_dict()['settings']['analysis']


def test_settings_are_saved():
    i = Index('i')
    i.settings(number_of_replicas=0)
    i.settings(number_of_shards=1)

    assert {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }
    } == i.to_dict()

def test_registered_doc_type_included_in_to_dict():
    i = Index('i', using='alias')
    i.doc_type(Post)

    assert Post._doc_type.index == 'i'
    assert {
        'mappings': {
            'doc': {
                'properties': {
                    'title': {'type': 'text'},
                    'published_from': {'type': 'date'},
                }
            }
        }
    } == i.to_dict()

def test_registered_doc_type_included_in_search():
    i = Index('i', using='alias')
    i.doc_type(Post)

    s = i.search()

    assert s._doc_type == [Post]


def test_aliases_add_to_object():
    random_alias = ''.join((choice(string.ascii_letters) for _ in range(100)))
    alias_dict = {random_alias: {}}

    index = Index('i', using='alias')
    index.aliases(**alias_dict)

    assert index._aliases == alias_dict


def test_aliases_returned_from_to_dict():
    random_alias = ''.join((choice(string.ascii_letters) for _ in range(100)))
    alias_dict = {random_alias: {}}

    index = Index('i', using='alias')
    index.aliases(**alias_dict)

    assert index._aliases == index.to_dict()['aliases'] == alias_dict


def test_analyzers_added_to_object():
    random_analyzer_name = ''.join((choice(string.ascii_letters) for _ in range(100)))
    random_analyzer = analyzer(random_analyzer_name, tokenizer="standard", filter="standard")

    index = Index('i', using='alias')
    index.analyzer(random_analyzer)

    assert index._analysis["analyzer"][random_analyzer_name] == {"filter": ["standard"], "type": "custom", "tokenizer": "standard"}


def test_analyzers_returned_from_to_dict():
    random_analyzer_name = ''.join((choice(string.ascii_letters) for _ in range(100)))
    random_analyzer = analyzer(random_analyzer_name, tokenizer="standard", filter="standard")
    index = Index('i', using='alias')
    index.analyzer(random_analyzer)

    assert index.to_dict()["settings"]["analysis"]["analyzer"][random_analyzer_name] == {"filter": ["standard"], "type": "custom", "tokenizer": "standard"}
