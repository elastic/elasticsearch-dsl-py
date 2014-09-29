from elasticsearch_dsl import DocType, Field


user_field = Field('object')
user_field.property('name', 'string', fields={'raw': Field('string', index='not_analyzed')})

class Repos(DocType):
    owner = user_field
    created_at = Field('date')
    description = Field('string', analyzer='snowball')
    tags = Field('string', index='not_analyzed')

    class Meta:
        index = 'git'

def test_get(data_client):
    elasticsearch_repo = Repos.get('elasticsearch-dsl-py')

    assert isinstance(elasticsearch_repo, Repos)
    assert elasticsearch_repo.owner.name == 'elasticsearch'

def test_search(data_client):
    assert Repos.search().count() == 1
