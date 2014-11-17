Search DSL
==========

The ``Search`` object
---------------------

The ``Search`` object represents the entire search request:

  * queries

  * filters

  * aggregations

  * sort

  * pagination

  * additional parameters

  * associated client


The API is designed to be chainable. With the exception of the
aggregations functionality this means that the ``Search`` object is immutable -
all changes to the object will result in a copy being created which contains
the changes. This means you can safely pass the ``Search`` object to foreign
code without fear of it modifying your objects.

You can pass an instance of the low-level `elasticsearch client <http://elasticsearch-py.readthedocs.org/>`_ when
instantiating the ``Search`` object::

    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search

    client = Elasticsearch()

    s = Search(client)

You can also define the client at a later time (for more options see the
~:ref:`connections` chapter)::

    s = s.using(client)

.. note::

    All methods return a *copy* of the object, making it safe to pass to
    outside code.

The API is chainable, allowing you to combine multiple method calls in one
statement::

    s = Search().using(client).query("match", title="python")

To send the request to Elasticsearch::

    response = s.execute()

For debugging purposes you can serialize the ``Search`` object to a ``dict``
explicitly::

    print(s.to_dict())

Queries
~~~~~~~



The library provides classes for all Elasticsearch query types. Pass all the parameters as keyword arguments::

    from elasticsearch_dsl.query import Match

    # {"match": {"query": "python django", "field": "title", "operator": "or"}}
    Match(query='python django', field='title', operator='or')

You can use the ``Q`` shortcut to construct the instance using a name with
parameters or the raw ``dict``::

    Q("match", query='python django', field='title', operator='or')
    Q({"match": {"query": "python django", "field": "title", "operator": "or"}})

To add the query to the ``Search`` object, use the ``.query()`` method::

    q = Q("match", query='python django', field='title', operator='or')
    s = s.query(q)

The method also accepts all the parameters as the ``Q`` shortcut::

    s = s.query('match', query='python django', field='title', operator='or')


Query combination
^^^^^^^^^^^^^^^^^

Query objects can be combined using logical operators::

    Q("match", title='python') | Q("match", title='django')
    # {"bool": {"should": [...]}}

    Q("match", title='python') & Q("match", title='django')
    # {"bool": {"must": [...]}}

    ~Q("match", "title"="python")
    # {"bool": {"must_not": [...]}}

You can also use the ``+`` operator::

    Q("match", title='python') + Q("match", title='django')
    # {"bool": {"must": [...]}}

When using the ``+`` operator with ``Bool`` queries, it will merge them into a
single ``Bool`` query::

    Q("bool") + Q("bool")
    # {"bool": {"..."}} 

When you call the ``.query()`` method multiple times, the ``+`` operator will
be used internally::

    s = s.query().query()
    print(s.to_dict())
    # {"query": {"bool": {...}}}

If you want to have precise control over the query form, use the ``Q`` shortcut
to directly construct the combined query::

    q = Q('bool',
        must=[Q('match', title='python')],
        should=[Q(...), Q(...)],
        minimum_should_match=1
    )
    s = Search().query(q)


Filters
~~~~~~~

Filters behave similarly to queries - just use the ``F`` shortcut and
``.filter()`` method. When you use the ``.filter()`` method, the query will be
automatically wrapped in a ``filtered`` query.

If you want to use the post_filter element for faceted navigation, use the
``.post_filter()`` method.


Aggregations
~~~~~~~~~~~~

To define an aggregation, you can use the ``A`` shortcut::

    A('terms', field='tags')
    # {"terms": {"field": "tags"}}

To nest aggregations, you can use the ``.bucket()`` and ``.metric()`` methods::

    a = A('terms', field='category')
    # {'terms': {'field': 'category'}}

    a.metric('clicks_per_category', 'sum', field='clicks').bucket('tags_per_category', 'terms', field='tags')
    # {'terms': {'field': 'category'}, 'aggs': {'clicks_per_category': {'sum': {'field': 'clicks'}}, 'tags_per_category': {'terms': {'field': 'tags'}}}}

To add aggregations to the ``Search`` object, use the ``.aggs`` property, which
acts as a top-level aggregation::

    s = Search()
    s.aggs.bucket('per_category', 'terms', field='category').metric('clicks_per_category', 'sum', field='clicks').bucket('tags_per_category', 'terms', field='tags')

    s.to_dict()
    # {'aggs': {'per_category': {'terms': {'field': 'category'}, 'aggs': {'clicks_per_category': {'sum': {'field': 'clicks'}}, 'tags_per_category': {'terms': {'field': 'tags'}}}}}}


You can access an existing bucket by its name::

    s = Search()

    s.aggs.bucket('per_category', 'terms', field='category')
    s.aggs['per_category'].metric('clicks_per_category', 'sum', field='clicks')
    s.aggs['per_category'].bucket('tags_per_category', 'terms', field='tags')

.. note::

    When chaining multiple aggregations, there is a difference between what
    ``.bucket()`` and ``.metric()`` methods return - ``.bucket()`` returns the
    newly defined bucket while ``.metric()`` returns its parent bucket to allow
    further chaining.

As opposed to other methods on the ``Search`` objects, defining aggregations is
done in-place (does not return a copy).


Sorting
~~~~~~~

To specify sorting order, use the ``.sort()`` method::

    s = Search().sort(
        'category',
        '-title',
        {"lines" : {"order" : "asc", "mode" : "avg"}}
    )

It accepts positional arguments which can be either strings or dictionaries.
String value is a field name, optionally prefixed by the ``-`` sign to specify
a descending order.

To reset the sorting, just call the method with no arguments::

  s = s.sort()


Pagination
~~~~~~~~~~

To specify the from/size parameters, use the Python slicing API::

  s = s[10:20]
  # {"from": 10, "size": 10}


Extra properties and parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To set extra properties of the search request, use the ``.extra()`` method::

  s = s.extra(explain=True)
 
To set query parameters, use the ``.params()`` method::

  s = s.params(search_type="count")


Serialization and Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The search object can be serialized into a dictionary by using the
``.to_dict()`` method.

You can also create a ``Search`` object from a ``dict``::

  s = Search.from_dict({"query": {"match": {"title": "python"}}})


Response
--------

You can execute your search by calling the ``.execute()`` method that will return
a ``Response`` object::

  response = s.execute()

  print(response.success())
  # True
      
  print(response.took)
  # 12


Hits
~~~~

To access to the hits returned by the search, access the ``hits`` property or
just iterate over the ``Response`` object::

    response = s.execute()
    print('Total %d hits found.' % response.hits.total)
    for h in response:
        print(h.title, h.body)


Result
~~~~~~

The individual hits is wrapped in a convenience class that allows attribute
access to the keys in the returned dictionary. All the metadata for the results
are accessible via ``_meta`` (without the leading ``_``)::

    response = s.execute()
    h = response.hits[0]
    print('/%s/%s/%s returned with score %f' % (
        h._meta.index, h._meta.doc_type, h._meta.id, h._meta.score))


Aggregations
~~~~~~~~~~~~

Aggregations are available through the ``aggregations`` property::

    for tag in response.aggregations.per_tag.buckets:
        print(tag.key, tag.max_lines.value)
    

