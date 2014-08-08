Elasticsearch DSL
=================

Elasticsearch DSL is a high-level library whose aim is to help with writing and
running queries against Elasticsearch. It is built on top of the official
low-level client (``elasticsearch-py``).


Philosophy
----------

The DSL inroduced in this library is trying to stay close to the terminology
and strucutre of the actual JSON DSL used by Elasticsearch; it doesn't try to
invent a new DSL, instead it aims at providing a more convenient way how to
write, and manipulate, queries without limiting you to a subset of
functionality. Since it uses the same terminology and building blocks no
special knowledge, on top of familiarity with the query DSL, should be
required.


Example
-------

With the low-level client you would write something like this:

.. code:: python

    from elasticsearch import Elasticsearch
    es = Elasticsearch()

    response = es.search(
        index="my-index",
        body={
          "query": {
            "filtered": {
              "query": {
                "bool": {
                  "must": [{"match": {"title": "python"}}],
                  "must_not": [{"match": {"description": "beta"}}]
                }
              },
              "filter": {"term": {"category": "search"}}
            }
          },
          "aggs" : {
            "per_tag": {
              "terms": {"field": "tags"},
              "aggs": {
                "max_lines": {"max": {"field": "lines"}}
              }
            }
          }
        }
    )
    for hit in response['hits']['hits']:
        print(hit['_score'], hit['_source']['title'])

Which could be very hard to modify (imagine adding another filter to that
query) and is definitely no fun to write. With the python DSL you can write the
same query as:

.. code:: python

    from elasticsearch_dsl import Search, Q

    s = Search(using=es).index("my-index") \
        .filter("term", category="search") \
        .query("match", title="python")   \
        .query(~Q("match", description="beta"))

    s.aggs.bucket('per_tag', 'terms', field='tags')\
        .metric('max_lines', 'max', field='lines')

    response = s.execute()
    for hit in response:
        print(hit._meta.score, hit.title)

    for b in response.aggregations.per_tag.buckets:
        print(b.key, b.max_lines.value)

The library will take care of:

  * composing queries/filters into compound queries/filters

  * creating filtered queries when ``.filter()`` has been used

  * providing a convenient wrapper around responses

  * no curly or square brackets everywhere!


Migration
---------

If you already have existing code using the ``elasticsearch-py`` library you
can easily start using this DSL without committing to porting your entire
application. You can create the ``Search`` object from current query dict, work
with it and, at the end, serialize it back to dict to send over the wire:

.. code:: python

    body = {...} # insert complicated query here
    # convert to search
    s = Search.from_dict(body)
    # add some filters, aggregations, queries, ...
    s.filter("term", tags="python")
    # optionally convert back to dict to plug back into existing code
    body = s.to_dict()

Since the DSL is built on top of the low-level client there should be nothing
stopping you from using your existing code or just dropping down to the low
level API whenever required; for example for all the APIs not (yet) covered by
the DSL.


License
-------

Copyright 2013 Elasticsearch

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

