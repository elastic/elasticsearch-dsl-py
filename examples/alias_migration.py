"""
Simple example with a single DocType demonstrating how schema can be managed,
including upgrading with reindexing.
"""
from datetime import datetime
from fnmatch import fnmatch

from elasticsearch_dsl import Document, Date, Text, Keyword, connections

ALIAS = 'test-blog'
PATTERN = ALIAS + '-*'

connections.create_connection()

class BlogPost(Document):
    title = Text()
    published = Date()
    tags = Keyword(multi=True)
    content = Text()

    def is_published(self):
        return datetime.now() > self.published

    @classmethod
    def _matches(cls, hit):
        # override _matches to match indices in a pattern instead of just ALIAS
        return fnmatch(hit['_index'], PATTERN)

    class Index:
        # we will use an alias instead of the index
        name = ALIAS
        # set settings and possibly other attributes
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

def setup():
    """
    Create the index template in elasticsearch specifying the mappings and any
    settings to be used. This can be run at any time, ideally at every new code
    deploy.
    """
    # create an index template
    index_template = BlogPost._index.as_template(ALIAS, PATTERN)
    # upload the template into elasticsearch
    # potentially overriding the one already there
    index_template.save()

    # create the first index if it doesn't exist
    if not BlogPost._index.exists():
        migrate(move_data=False)

def migrate(move_data=True, update_alias=True):
    """
    Upgrade function that creates a new index for the data. Optionally it also can
    (and by default will) reindex previous copy of the data into the new index
    (specify ``move_data=False`` to skip this step) and update the alias to
    point to the latest index (set ``update_alias=False`` to skip).

    Note that while this function is running the application can still perform
    any and all searches without any loss of functionality. It should, however,
    not perform any writes at this time as those might be lost.
    """
    # construct a new index name by appending current timestamp
    next_index = PATTERN.replace('*', datetime.now().strftime('%Y%m%d%H%M%S%f'))

    # get the low level connection
    es = connections.get_connection()

    # create new index, it will use the settings from the template
    es.indices.create(index=next_index)

    if move_data:
        # move data from current alias to the new index
        es.reindex(
            body={"source": {"index": ALIAS}, "dest": {"index": next_index}},
            request_timeout=3600
        )
        # refresh the index to make the changes visible
        es.indices.refresh(index=next_index)

    if update_alias:
        # repoint the alias to point to the newly created index
        es.indices.update_aliases(body={
            'actions': [
                {"remove": {"alias": ALIAS, "index": PATTERN}},
                {"add": {"alias": ALIAS, "index": next_index}},
            ]
        })
