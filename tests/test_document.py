#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import codecs
import ipaddress
import pickle
from datetime import datetime
from hashlib import md5

from pytest import raises

from elasticsearch_dsl import (
    Index,
    InnerDoc,
    Mapping,
    Range,
    analyzer,
    document,
    field,
    utils,
)
from elasticsearch_dsl.exceptions import IllegalOperation, ValidationException


class MyInner(InnerDoc):
    old_field = field.Text()


class MyDoc(document.Document):
    title = field.Keyword()
    name = field.Text()
    created_at = field.Date()
    inner = field.Object(MyInner)


class MySubDoc(MyDoc):
    name = field.Keyword()

    class Index:
        name = "default-index"


class MyDoc2(document.Document):
    extra = field.Long()


class MyMultiSubDoc(MyDoc2, MySubDoc):
    pass


class Comment(document.InnerDoc):
    title = field.Text()
    tags = field.Keyword(multi=True)


class DocWithNested(document.Document):
    comments = field.Nested(Comment)

    class Index:
        name = "test-doc-with-nested"


class SimpleCommit(document.Document):
    files = field.Text(multi=True)

    class Index:
        name = "test-git"


class Secret(str):
    pass


class SecretField(field.CustomField):
    builtin_type = "text"

    def _serialize(self, data):
        return codecs.encode(data, "rot_13")

    def _deserialize(self, data):
        if isinstance(data, Secret):
            return data
        return Secret(codecs.decode(data, "rot_13"))


class SecretDoc(document.Document):
    title = SecretField(index="no")

    class Index:
        name = "test-secret-doc"


class NestedSecret(document.Document):
    secrets = field.Nested(SecretDoc)

    class Index:
        name = "test-nested-secret"


class OptionalObjectWithRequiredField(document.Document):
    comments = field.Nested(properties={"title": field.Keyword(required=True)})

    class Index:
        name = "test-required"


class Host(document.Document):
    ip = field.Ip()

    class Index:
        name = "test-host"


def test_range_serializes_properly():
    class D(document.Document):
        lr = field.LongRange()

    d = D(lr=Range(lt=42))
    assert 40 in d.lr
    assert 47 not in d.lr
    assert {"lr": {"lt": 42}} == d.to_dict()

    d = D(lr={"lt": 42})
    assert {"lr": {"lt": 42}} == d.to_dict()


def test_range_deserializes_properly():
    class D(document.InnerDoc):
        lr = field.LongRange()

    d = D.from_es({"lr": {"lt": 42}}, True)
    assert isinstance(d.lr, Range)
    assert 40 in d.lr
    assert 47 not in d.lr


def test_resolve_nested():
    nested, field = NestedSecret._index.resolve_nested("secrets.title")
    assert nested == ["secrets"]
    assert field is NestedSecret._doc_type.mapping["secrets"]["title"]


def test_conflicting_mapping_raises_error_in_index_to_dict():
    class A(document.Document):
        name = field.Text()

    class B(document.Document):
        name = field.Keyword()

    i = Index("i")
    i.document(A)
    i.document(B)

    with raises(ValueError):
        i.to_dict()


def test_ip_address_serializes_properly():
    host = Host(ip=ipaddress.IPv4Address(u"10.0.0.1"))

    assert {"ip": "10.0.0.1"} == host.to_dict()


def test_matches_uses_index():
    assert SimpleCommit._matches({"_index": "test-git"})
    assert not SimpleCommit._matches({"_index": "not-test-git"})


def test_matches_with_no_name_always_matches():
    class D(document.Document):
        pass

    assert D._matches({})
    assert D._matches({"_index": "whatever"})


def test_matches_accepts_wildcards():
    class MyDoc(document.Document):
        class Index:
            name = "my-*"

    assert MyDoc._matches({"_index": "my-index"})
    assert not MyDoc._matches({"_index": "not-my-index"})


def test_assigning_attrlist_to_field():
    sc = SimpleCommit()
    l = ["README", "README.rst"]
    sc.files = utils.AttrList(l)

    assert sc.to_dict()["files"] is l


def test_optional_inner_objects_are_not_validated_if_missing():
    d = OptionalObjectWithRequiredField()

    assert d.full_clean() is None


def test_custom_field():
    s = SecretDoc(title=Secret("Hello"))

    assert {"title": "Uryyb"} == s.to_dict()
    assert s.title == "Hello"

    s = SecretDoc.from_es({"_source": {"title": "Uryyb"}})
    assert s.title == "Hello"
    assert isinstance(s.title, Secret)


def test_custom_field_mapping():
    assert {
        "properties": {"title": {"index": "no", "type": "text"}}
    } == SecretDoc._doc_type.mapping.to_dict()


def test_custom_field_in_nested():
    s = NestedSecret()
    s.secrets.append(SecretDoc(title=Secret("Hello")))

    assert {"secrets": [{"title": "Uryyb"}]} == s.to_dict()
    assert s.secrets[0].title == "Hello"


def test_multi_works_after_doc_has_been_saved():
    c = SimpleCommit()
    c.full_clean()
    c.files.append("setup.py")

    assert c.to_dict() == {"files": ["setup.py"]}


def test_multi_works_in_nested_after_doc_has_been_serialized():
    # Issue #359
    c = DocWithNested(comments=[Comment(title="First!")])

    assert [] == c.comments[0].tags
    assert {"comments": [{"title": "First!"}]} == c.to_dict()
    assert [] == c.comments[0].tags


def test_null_value_for_object():
    d = MyDoc(inner=None)

    assert d.inner is None


def test_inherited_doc_types_can_override_index():
    class MyDocDifferentIndex(MySubDoc):
        class Index:
            name = "not-default-index"
            settings = {"number_of_replicas": 0}
            aliases = {"a": {}}
            analyzers = [analyzer("my_analizer", tokenizer="keyword")]

    assert MyDocDifferentIndex._index._name == "not-default-index"
    assert MyDocDifferentIndex()._get_index() == "not-default-index"
    assert MyDocDifferentIndex._index.to_dict() == {
        "aliases": {"a": {}},
        "mappings": {
            "properties": {
                "created_at": {"type": "date"},
                "inner": {
                    "type": "object",
                    "properties": {"old_field": {"type": "text"}},
                },
                "name": {"type": "keyword"},
                "title": {"type": "keyword"},
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {"my_analizer": {"tokenizer": "keyword", "type": "custom"}}
            },
            "number_of_replicas": 0,
        },
    }


def test_to_dict_with_meta():
    d = MySubDoc(title="hello")
    d.meta.routing = "some-parent"

    assert {
        "_index": "default-index",
        "_routing": "some-parent",
        "_source": {"title": "hello"},
    } == d.to_dict(True)


def test_to_dict_with_meta_includes_custom_index():
    d = MySubDoc(title="hello")
    d.meta.index = "other-index"

    assert {"_index": "other-index", "_source": {"title": "hello"}} == d.to_dict(True)


def test_to_dict_without_skip_empty_will_include_empty_fields():
    d = MySubDoc(tags=[], title=None, inner={})

    assert {} == d.to_dict()
    assert {"tags": [], "title": None, "inner": {}} == d.to_dict(skip_empty=False)


def test_attribute_can_be_removed():
    d = MyDoc(title="hello")

    del d.title
    assert "title" not in d._d_


def test_doc_type_can_be_correctly_pickled():
    d = DocWithNested(
        title="Hello World!", comments=[Comment(title="hellp")], meta={"id": 42}
    )
    s = pickle.dumps(d)

    d2 = pickle.loads(s)

    assert d2 == d
    assert 42 == d2.meta.id
    assert "Hello World!" == d2.title
    assert [{"title": "hellp"}] == d2.comments
    assert isinstance(d2.comments[0], Comment)


def test_meta_is_accessible_even_on_empty_doc():
    d = MyDoc()
    d.meta

    d = MyDoc(title="aaa")
    d.meta


def test_meta_field_mapping():
    class User(document.Document):
        username = field.Text()

        class Meta:
            all = document.MetaField(enabled=False)
            _index = document.MetaField(enabled=True)
            dynamic = document.MetaField("strict")
            dynamic_templates = document.MetaField([42])

    assert {
        "properties": {"username": {"type": "text"}},
        "_all": {"enabled": False},
        "_index": {"enabled": True},
        "dynamic": "strict",
        "dynamic_templates": [42],
    } == User._doc_type.mapping.to_dict()


def test_multi_value_fields():
    class Blog(document.Document):
        tags = field.Keyword(multi=True)

    b = Blog()
    assert [] == b.tags
    b.tags.append("search")
    b.tags.append("python")
    assert ["search", "python"] == b.tags


def test_docs_with_properties():
    class User(document.Document):
        pwd_hash = field.Text()

        def check_password(self, pwd):
            return md5(pwd).hexdigest() == self.pwd_hash

        @property
        def password(self):
            raise AttributeError("readonly")

        @password.setter
        def password(self, pwd):
            self.pwd_hash = md5(pwd).hexdigest()

    u = User(pwd_hash=md5(b"secret").hexdigest())
    assert u.check_password(b"secret")
    assert not u.check_password(b"not-secret")

    u.password = b"not-secret"
    assert "password" not in u._d_
    assert not u.check_password(b"secret")
    assert u.check_password(b"not-secret")

    with raises(AttributeError):
        u.password


def test_nested_can_be_assigned_to():
    d1 = DocWithNested(comments=[Comment(title="First!")])
    d2 = DocWithNested()

    d2.comments = d1.comments
    assert isinstance(d1.comments[0], Comment)
    assert d2.comments == [{"title": "First!"}]
    assert {"comments": [{"title": "First!"}]} == d2.to_dict()
    assert isinstance(d2.comments[0], Comment)


def test_nested_can_be_none():
    d = DocWithNested(comments=None, title="Hello World!")

    assert {"title": "Hello World!"} == d.to_dict()


def test_nested_defaults_to_list_and_can_be_updated():
    md = DocWithNested()

    assert [] == md.comments

    md.comments.append({"title": "hello World!"})
    assert {"comments": [{"title": "hello World!"}]} == md.to_dict()


def test_to_dict_is_recursive_and_can_cope_with_multi_values():
    md = MyDoc(name=["a", "b", "c"])
    md.inner = [MyInner(old_field="of1"), MyInner(old_field="of2")]

    assert isinstance(md.inner[0], MyInner)

    assert {
        "name": ["a", "b", "c"],
        "inner": [{"old_field": "of1"}, {"old_field": "of2"}],
    } == md.to_dict()


def test_to_dict_ignores_empty_collections():
    md = MySubDoc(name="", address={}, count=0, valid=False, tags=[])

    assert {"name": "", "count": 0, "valid": False} == md.to_dict()


def test_declarative_mapping_definition():
    assert issubclass(MyDoc, document.Document)
    assert hasattr(MyDoc, "_doc_type")
    assert {
        "properties": {
            "created_at": {"type": "date"},
            "name": {"type": "text"},
            "title": {"type": "keyword"},
            "inner": {"type": "object", "properties": {"old_field": {"type": "text"}}},
        }
    } == MyDoc._doc_type.mapping.to_dict()


def test_you_can_supply_own_mapping_instance():
    class MyD(document.Document):
        title = field.Text()

        class Meta:
            mapping = Mapping()
            mapping.meta("_all", enabled=False)

    assert {
        "_all": {"enabled": False},
        "properties": {"title": {"type": "text"}},
    } == MyD._doc_type.mapping.to_dict()


def test_document_can_be_created_dynamically():
    n = datetime.now()
    md = MyDoc(title="hello")
    md.name = "My Fancy Document!"
    md.created_at = n

    inner = md.inner
    # consistent returns
    assert inner is md.inner
    inner.old_field = "Already defined."

    md.inner.new_field = ["undefined", "field"]

    assert {
        "title": "hello",
        "name": "My Fancy Document!",
        "created_at": n,
        "inner": {"old_field": "Already defined.", "new_field": ["undefined", "field"]},
    } == md.to_dict()


def test_invalid_date_will_raise_exception():
    md = MyDoc()
    md.created_at = "not-a-date"
    with raises(ValidationException):
        md.full_clean()


def test_document_inheritance():
    assert issubclass(MySubDoc, MyDoc)
    assert issubclass(MySubDoc, document.Document)
    assert hasattr(MySubDoc, "_doc_type")
    assert {
        "properties": {
            "created_at": {"type": "date"},
            "name": {"type": "keyword"},
            "title": {"type": "keyword"},
            "inner": {"type": "object", "properties": {"old_field": {"type": "text"}}},
        }
    } == MySubDoc._doc_type.mapping.to_dict()


def test_child_class_can_override_parent():
    class A(document.Document):
        o = field.Object(dynamic=False, properties={"a": field.Text()})

    class B(A):
        o = field.Object(dynamic="strict", properties={"b": field.Text()})

    assert {
        "properties": {
            "o": {
                "dynamic": "strict",
                "properties": {"a": {"type": "text"}, "b": {"type": "text"}},
                "type": "object",
            }
        }
    } == B._doc_type.mapping.to_dict()


def test_meta_fields_are_stored_in_meta_and_ignored_by_to_dict():
    md = MySubDoc(meta={"id": 42}, name="My First doc!")

    md.meta.index = "my-index"
    assert md.meta.index == "my-index"
    assert md.meta.id == 42
    assert {"name": "My First doc!"} == md.to_dict()
    assert {"id": 42, "index": "my-index"} == md.meta.to_dict()


def test_index_inheritance():
    assert issubclass(MyMultiSubDoc, MySubDoc)
    assert issubclass(MyMultiSubDoc, MyDoc2)
    assert issubclass(MyMultiSubDoc, document.Document)
    assert hasattr(MyMultiSubDoc, "_doc_type")
    assert hasattr(MyMultiSubDoc, "_index")
    assert {
        "properties": {
            "created_at": {"type": "date"},
            "name": {"type": "keyword"},
            "title": {"type": "keyword"},
            "inner": {"type": "object", "properties": {"old_field": {"type": "text"}}},
            "extra": {"type": "long"},
        }
    } == MyMultiSubDoc._doc_type.mapping.to_dict()


def test_meta_fields_can_be_set_directly_in_init():
    p = object()
    md = MyDoc(_id=p, title="Hello World!")

    assert md.meta.id is p


def test_save_no_index(mock_client):
    md = MyDoc()
    with raises(ValidationException):
        md.save(using="mock")


def test_delete_no_index(mock_client):
    md = MyDoc()
    with raises(ValidationException):
        md.delete(using="mock")


def test_update_no_fields():
    md = MyDoc()
    with raises(IllegalOperation):
        md.update()


def test_search_with_custom_alias_and_index(mock_client):
    search_object = MyDoc.search(
        using="staging", index=["custom_index1", "custom_index2"]
    )

    assert search_object._using == "staging"
    assert search_object._index == ["custom_index1", "custom_index2"]


def test_from_es_respects_underscored_non_meta_fields():
    doc = {
        "_index": "test-index",
        "_id": "elasticsearch",
        "_score": 12.0,
        "fields": {"hello": "world", "_routing": "es", "_tags": ["search"]},
        "_source": {
            "city": "Amsterdam",
            "name": "Elasticsearch",
            "_tagline": "You know, for search",
        },
    }

    class Company(document.Document):
        class Index:
            name = "test-company"

    c = Company.from_es(doc)

    assert c.meta.fields._tags == ["search"]
    assert c.meta.fields._routing == "es"
    assert c._tagline == "You know, for search"


def test_nested_and_object_inner_doc():
    class MySubDocWithNested(MyDoc):
        nested_inner = field.Nested(MyInner)

    props = MySubDocWithNested._doc_type.mapping.to_dict()["properties"]
    assert props == {
        "created_at": {"type": "date"},
        "inner": {"properties": {"old_field": {"type": "text"}}, "type": "object"},
        "name": {"type": "text"},
        "nested_inner": {
            "properties": {"old_field": {"type": "text"}},
            "type": "nested",
        },
        "title": {"type": "keyword"},
    }
