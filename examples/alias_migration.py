"""
Simple example with a single DocType demonstrating how schema can be managed,
including upgrading with reindexing.
"""
from datetime import datetime

from elasticsearch_dsl import DocType, Date, Text, Keyword, IndexTemplate, \
    connections

ALIAS = 'blog'
PATTERN = ALIAS + '-*'

connections.create_connection()

class BlogPost(DocType):
    title = Text()
    published = Date()
    tags = Keyword(multi=True)
    content = Text()

    def is_published(self):
        return datetime.now() > self.published

    class Meta:
        index = ALIAS

def setup():
    """
    Create the index template in elasticsearch specifying the mappings and any
    settings to be used. This can be run at any time, ideally at every new code
    deploy.
    """
    # create an index template
    index_template = IndexTemplate(PATTERN, ALIAS)
    # add the DocType mappings
    index_template.doc_type(BlogPost)
    # set settings and possibly other attributes
    index_template.settings(
        number_of_shards=1,
        number_of_replicas=0
    )
    # upload the template into elasticsearch
    # potentially overriding the one already there
    index_template.save()

    # get the low level connection
    es = connections.get_connection()
    # create the first index if it doesn't exist
    if not es.indices.exists_alias(ALIAS):
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
    # get the low level connection
    es = connections.get_connection()
    # retrieve the list of indices matching the pattern...
    indices = es.cat.indices(index=PATTERN, h='index').split()
    # ... and extract the index versions
    versions = (int(i[len(PATTERN)-1:]) for i in indices)
    # construct a new index name
    next_index = PATTERN.replace('*', str(max(versions, default=0) + 1))

    # create new index, it will use the settings from the template
    es.indices.create(index=next_index)

    if move_data:
        # move data from current alias to the new index
        es.reindex(
            body={"source": {"index": ALIAS}, "dest": {"index": next_index}},
            request_timeout=3600
        )

    if update_alias:
        # repoint the alias to point to the newly created index
        es.indices.update_aliases(body={
            'actions': [
                {"remove": {"alias": ALIAS, "index": PATTERN}},
                {"add": {"alias": ALIAS, "index": next_index}},
            ]
        })
