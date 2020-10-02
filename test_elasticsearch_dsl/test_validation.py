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

from datetime import datetime

from pytest import raises

from elasticsearch_dsl import (
    Boolean,
    Date,
    Document,
    InnerDoc,
    Integer,
    Nested,
    Object,
    Text,
)
from elasticsearch_dsl.exceptions import ValidationException


class Author(InnerDoc):
    name = Text(required=True)
    email = Text(required=True)

    def clean(self):
        print(self, type(self), self.name)
        if self.name.lower() not in self.email:
            raise ValidationException("Invalid email!")


class BlogPost(Document):
    authors = Nested(Author, required=True)
    created = Date()
    inner = Object()


class BlogPostWithStatus(Document):
    published = Boolean(required=True)


class AutoNowDate(Date):
    def clean(self, data):
        if data is None:
            data = datetime.now()
        return super(AutoNowDate, self).clean(data)


class Log(Document):
    timestamp = AutoNowDate(required=True)
    data = Text()


def test_required_int_can_be_0():
    class DT(Document):
        i = Integer(required=True)

    dt = DT(i=0)
    assert dt.full_clean() is None


def test_required_field_cannot_be_empty_list():
    class DT(Document):
        i = Integer(required=True)

    dt = DT(i=[])
    with raises(ValidationException):
        dt.full_clean()


def test_validation_works_for_lists_of_values():
    class DT(Document):
        i = Date(required=True)

    dt = DT(i=[datetime.now(), "not date"])
    with raises(ValidationException):
        dt.full_clean()

    dt = DT(i=[datetime.now(), datetime.now()])
    assert None is dt.full_clean()


def test_field_with_custom_clean():
    l = Log()
    l.full_clean()

    assert isinstance(l.timestamp, datetime)


def test_empty_object():
    d = BlogPost(authors=[{"name": "Honza", "email": "honza@elastic.co"}])
    d.inner = {}

    d.full_clean()


def test_missing_required_field_raises_validation_exception():
    d = BlogPost()
    with raises(ValidationException):
        d.full_clean()

    d = BlogPost()
    d.authors.append({"name": "Honza"})
    with raises(ValidationException):
        d.full_clean()

    d = BlogPost()
    d.authors.append({"name": "Honza", "email": "honza@elastic.co"})
    d.full_clean()


def test_boolean_doesnt_treat_false_as_empty():
    d = BlogPostWithStatus()
    with raises(ValidationException):
        d.full_clean()
    d.published = False
    d.full_clean()
    d.published = True
    d.full_clean()


def test_custom_validation_on_nested_gets_run():
    d = BlogPost(authors=[Author(name="Honza", email="king@example.com")], created=None)

    assert isinstance(d.authors[0], Author)

    with raises(ValidationException):
        d.full_clean()


def test_accessing_known_fields_returns_empty_value():
    d = BlogPost()

    assert [] == d.authors

    d.authors.append({})
    assert None is d.authors[0].name
    assert None is d.authors[0].email


def test_empty_values_are_not_serialized():
    d = BlogPost(authors=[{"name": "Honza", "email": "honza@elastic.co"}], created=None)

    d.full_clean()
    assert d.to_dict() == {"authors": [{"name": "Honza", "email": "honza@elastic.co"}]}
