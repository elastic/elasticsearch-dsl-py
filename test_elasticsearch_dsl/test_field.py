from elasticsearch_dsl import field


def test_field_from_dict():
    f = field.construct_field({'type': 'string', 'index': 'not_analyzed'})

    assert isinstance(f, field.String)
    assert {'type': 'string', 'index': 'not_analyzed'} == f.to_dict()


def test_multi_fields_are_accepted_and_parsed():
    f = field.construct_field(
        'string',
        fields={
            'raw': {'type': 'string', 'index': 'not_analyzed'},
            'eng': field.String(analyzer='english'),
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
    f.field('name', 'string', index='not_analyzed')

    assert {
        'type': 'nested',
        'properties': {
            'name': {'type': 'string', 'index': 'not_analyzed'}
        },
    } == f.to_dict()

def test_nested_provides_direct_access_to_its_fields():
    f = field.Nested()
    f.field('name', 'string', index='not_analyzed')

    assert 'name' in f
    assert f['name'] == field.String(index='not_analyzed')
