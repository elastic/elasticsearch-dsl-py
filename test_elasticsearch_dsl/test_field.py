from datetime import datetime
from dateutil import tz

import pytest

from elasticsearch_dsl import field

def test_boolean_deserialization():
    bf = field.Boolean()

    assert not bf.deserialize("false")
    assert not bf.deserialize(False)
    assert not bf.deserialize("")
    assert not bf.deserialize(0)

    assert bf.deserialize(True)
    assert bf.deserialize("true")
    assert bf.deserialize(1)

def test_date_field_can_have_default_tz():
    f = field.Date(default_timezone='UTC')
    now = datetime.now()

    now_with_tz = f._deserialize(now)

    assert now_with_tz.tzinfo == tz.gettz('UTC')
    assert now.isoformat() + '+00:00' == now_with_tz.isoformat()

    now_with_tz = f._deserialize(now.isoformat())

    assert now_with_tz.tzinfo == tz.gettz('UTC')
    assert now.isoformat() + '+00:00' == now_with_tz.isoformat()

def test_custom_field_car_wrap_other_field():
    class MyField(field.CustomField):
        @property
        def builtin_type(self):
            return field.Text(**self._params)

    assert {'type': 'text', 'index': 'not_analyzed'} == MyField(index='not_analyzed').to_dict()

def test_field_from_dict():
    f = field.construct_field({'type': 'text', 'index': 'not_analyzed'})

    assert isinstance(f, field.Text)
    assert {'type': 'text', 'index': 'not_analyzed'} == f.to_dict()


def test_multi_fields_are_accepted_and_parsed():
    f = field.construct_field(
        'text',
        fields={
            'raw': {'type': 'keyword'},
            'eng': field.Text(analyzer='english'),
        }
    )

    assert isinstance(f, field.Text)
    assert {
        'type': 'text',
        'fields': {
            'raw': {'type': 'keyword'},
            'eng': {'type': 'text', 'analyzer': 'english'},
        }
    } == f.to_dict()

def test_modifying_nested():
    f = field.Nested()
    f.field('name', 'text', index='not_analyzed')

    assert {
        'type': 'nested',
        'properties': {
            'name': {'type': 'text', 'index': 'not_analyzed'}
        },
    } == f.to_dict()

def test_nested_provides_direct_access_to_its_fields():
    f = field.Nested()
    f.field('name', 'text', index='not_analyzed')

    assert 'name' in f
    assert f['name'] == field.Text(index='not_analyzed')


def test_field_supports_multiple_analyzers():
    f = field.Text(analyzer='snowball', search_analyzer='keyword')
    assert {'analyzer': 'snowball', 'search_analyzer': 'keyword', 'type': 'text'} == f.to_dict()


def test_multifield_supports_multiple_analyzers():
    f = field.Text(fields={
        'f1': field.Text(search_analyzer='keyword', analyzer='snowball'),
        'f2': field.Text(analyzer='keyword')
    })
    assert {
       'fields': {
           'f1': {'analyzer': 'snowball',
                  'search_analyzer': 'keyword',
                  'type': 'text'
           },
           'f2': {
               'analyzer': 'keyword', 'type': 'text'}
       },
       'type': 'text'
    } == f.to_dict()


def test_scaled_float():
    with pytest.raises(TypeError):
        field.ScaledFloat()
    f = field.ScaledFloat(123)
    assert f.to_dict() == {'scaling_factor': 123, 'type': 'scaled_float'}
