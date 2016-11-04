from datetime import datetime

from elasticsearch_dsl import DocType, Nested, Text, Date, Object, Boolean, Integer
from elasticsearch_dsl.field import InnerObjectWrapper
from elasticsearch_dsl.exceptions import ValidationException

from pytest import raises

class Author(InnerObjectWrapper):
    def clean(self):
        if self.name.lower() not in self.email:
            raise ValidationException('Invalid email!')

class BlogPost(DocType):
    authors = Nested(
        required=True,
        doc_class=Author,
        properties={
            'name': Text(required=True),
            'email': Text(required=True)
        }
    )
    created = Date()
    inner = Object()


class BlogPostWithStatus(DocType):
    published = Boolean(required=True)


class AutoNowDate(Date):
    def clean(self, data):
        if data is None:
            data = datetime.now()
        return super(AutoNowDate, self).clean(data)

class Log(DocType):
    timestamp = AutoNowDate(required=True)
    data = Text()

def test_required_int_can_be_0():
    class DT(DocType):
        i = Integer(required=True)

    dt = DT(i=0)
    assert dt.full_clean() is None

def test_required_field_cannot_be_empty_list():
    class DT(DocType):
        i = Integer(required=True)

    dt = DT(i=[])
    with raises(ValidationException):
        dt.full_clean()

def test_validation_works_for_lists_of_values():
    class DT(DocType):
        i = Date(required=True)

    with raises(ValidationException):
        DT(i=[datetime.now(), 'not date'])

    dt = DT(i=[datetime.now(), datetime.now()])
    assert None is dt.full_clean()


def test_field_with_custom_clean():
    l = Log()
    l.full_clean()

    assert isinstance(l.timestamp, datetime)

def test_empty_object():
    d = BlogPost(authors=[{'name': 'Honza', 'email': 'honza@elastic.co'}])
    d.inner = {}

    d.full_clean()

def test_missing_required_field_raises_validation_exception():
    d = BlogPost()
    with raises(ValidationException):
        d.full_clean()

    d = BlogPost()
    d.authors.append({'name': 'Honza'})
    with raises(ValidationException):
        d.full_clean()

    d = BlogPost()
    d.authors.append({'name': 'Honza', 'email': 'honza@elastic.co'})
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
    d = BlogPost(authors=[{'name': 'Honza', 'email': 'king@example.com'}], created=None)

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
    d = BlogPost(authors=[{'name': 'Honza', 'email': 'honza@elastic.co'}], created=None)

    d.full_clean()
    assert d.to_dict() == {
        'authors': [{'name': 'Honza', 'email': 'honza@elastic.co'}]
    }
