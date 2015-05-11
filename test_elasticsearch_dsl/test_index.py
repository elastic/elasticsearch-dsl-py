from elasticsearch_dsl import DocType, Index, String, Date

from random import choice

import string

class Post(DocType):
    title = String()
    published_from = Date()


def test_search_is_limited_to_index_name():
    i = Index('my-index')
    s = i.search()

    assert s._index == ['my-index']

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
            'post': {
                'properties': {
                    'title': {'type': 'string'},
                    'published_from': {'type': 'date'},
                }
            }
        }
    } == i.to_dict()

def test_registered_doc_type_included_in_search():
    i = Index('i', using='alias')
    i.doc_type(Post)

    s = i.search()

    assert s._doc_type_map == {'post': Post.from_es}


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
