from elasticsearch_dsl import field


def test_field_from_dict():
    f = field.Field({'type': 'string', 'index': 'not_analyzed'})

    assert isinstance(f, field.String)
    assert {'type': 'string', 'index': 'not_analyzed'} == f.to_dict()


def test_multi_fields_are_accepted_and_parsed():
    f = field.Field(
        'string',
        fields={
            'raw': {'type': 'string', 'index': 'not_analyzed'},
            'eng': field.Field('string', analyzer='english'),
        }
    )

    assert isinstance(f, field.String)
    assert {
        'type': 'string',
        'fields': {
            'raw': { 'type': 'string', 'index': 'not_analyzed'},
            'eng': { 'type': 'string', 'analyzer': 'english'},
        }
    } == f.to_dict()

def test_modifying_nested():
    f = field.Nested()
    f = f.property('name', 'string', index='not_analyzed')

    assert {
        'type': 'nested',
        'properties': {
            'name': {'type': 'string', 'index': 'not_analyzed'}
        },
    } == f.to_dict()
