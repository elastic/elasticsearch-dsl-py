Elasticsearch Python DSL
========================

Elasticsearch DSL is a high-level library whose aim is to help with writing and
running queries against Elasticsearch. It is built on top of the official
low-level client (``elasticsearch-py``).

The DSL inroduced in this library is trying to stay close to the terminology
and strucutre of the actual JSON DSL used by Elasticsearch; it doesn't try to
invent a new DSL, instead it aims at providing a more convenient way how to
write, and manipulate, queries without limiting you to a subset of
functionality. Since it uses the same terminology and building blocks no
special knowledge, on top of familiarity with the query DSL, should be
required.

Example::

    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search, Q

    es = Elasticsearch()

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


Search object
-------------

``Search`` object represents the entire search request, including the queries,
filters, aggregations and metadata like the associated client and pagination
info.

The search API is designed to be chainable. With the exception of the
aggregations functionality this means that the ``Search`` object is immutable -
all changes to the object will result in a copy being created which contains
the changes. This means you can safely pass the ``Search`` object to foreign
code without fear of it modifying your objects.

When instantiating the Search object you should pass in an instance of
``Elasticsearch`` - the low-level client::

    form elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search

    s = Search(es)

If you don't do this you can supply the client at later time by using the
``.using()`` method::

    s = s.using(es)


Querying
~~~~~~~~

Adding queries to a search is done via the ``.query`` method. By default it
will combine the query passed in with the query already associated with the
search. The query accepts any parameter combination that the ``Q`` shortcut
does:

* name of the query as string and it's parameters as keyword arguments - preferred
* ``Query`` object
* ``dict`` representing the query

The call to the ``.query()`` method will always return a copy of the ``Search``
object thus enabling you to chain any number of calls to this, or other,
method.

A query will be constructed from the parameters and then combined with the
query already defined in the ``Search`` object. The operator used for this is
``+`` which works like logical ``and`` operator with the exception of bool
queries where it just concatenates all of the internal lists (``must``,
``must_not`` and ``should``). In typical use case (just adding more query
conditions) this will produce the most optimal query - a single ``bool`` query
with all the core queries in the ``must`` list.

If you want to have precise control over the query form feel free to use the
``Q`` shortcut to directly construct your queries::

    q = Q('bool',
        must=[Q('match', title='python')],
        should=[Q(...), Q(...)],
        minimum_should_match=1
    )
    s = Search().query(q)


Filtering
~~~~~~~~~

The ``filter`` method is completely analogous to ``query``. By default, if a
filter is defined, the query will be turned into a ``filtered`` query with the
query and filter taken from the ``Search`` object.

If you wish to use the top-level filter, use the ``post_filter`` method.


Aggregations
~~~~~~~~~~~~

You can specify aggregations as part of your search through the ``.aggs``
property. There are two methods on the property - ``bucket`` and ``metric``::

    s = Search()

    # define a global metric:
    s.aggs.metric("max_size", "max", field='size')

    # define a bucket aggregation and metrics inside:
    s.aggs.bucket('per_country', 'terms', field='country_code')\
        .metric('max_size', 'max', field='size') \
        .metric('min_size', 'min', field='size')

    # you can also retrieve existing bucket and start there:
    s.aggs['per_country'].bucket('per_city', 'terms', field='city')
    s.aggs['per_country']['per_city'].metric('...')

The aggregation methods are chainable to allow you to specify multiple steps in
a single call. The way that ``bucket`` and ``metric`` behave is slightly
different though - call to ``bucket`` will return the bucket so any chained
aggregations will be defined inside the newly created bucket. Calls to
``metric`` on the other hand will return the metric aggregation's bucket so all
subsequent chained calls will be defined *next* to the new metric aggregation.

Note that defining aggregations is done in-place for ``Search`` objects due to
the different chaining schema.

(de)serialization
~~~~~~~~~~~~~~~~~

The search object can be serialized (and will be internally upon execution)
into a dictionary by using the ``.to_dict()`` method. Reverse process is also
possible by using the class method ``.from_dict(body)``.

This can be most useful when migrating to/from legacy code which uses the
low-level class and has previously defined all the queries manually using
python ``dict``\ s. For example if you have an existing query that you wish to
continue using while maybe adding some filters to it::

    # previously used raw search body
    query = {'from': 0, 'query': {'filtered': {...}}, 'aggs': {...}}

    # create the search object and associate the client to it
    s = Search.from_dict(query).using(es)
    # now you can add filters/aggregations etc without problems
    s.filter('term', category='python')
    # and use the .execute() method to get access to the result class
    response = s.execute()


Response
--------

You can execute your search by calling the ``execute()`` method that will retun
a ``Response`` object.


Hits
~~~~

If you want access to the hits returned by the search, just iterate over the
response or access the ``hits`` property. It contains both the hits and the
associated metadata like ``total`` and ``max_score``::

    s = Search()
    response = s.execute()
    print('Total %d hits found.' % response.hits.total)
    for h in response:
        print(h.title, h.body)


Result
~~~~~~

All individual hits (as well as the entire response) is wrapped in a
convenience class that allows attribute access to the keys in the returned
dictionary. All the metadata for the results are accessible via ``_meta``
(without the leading ``_``)::

    h = response.hits[0]
    print('/%s/%s/%s returned with score %f' % (
        h._meta.index, h._meta.doc_type, h._meta.id, h._meta.score))


Aggregations
~~~~~~~~~~~~

Aggregation results are presented as-is with only the attribute access added
for convenience.


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


Contents
--------

.. toctree::
   :maxdepth: 2

   Changelog

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`

