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

You can pass an instance of the low-level `elasticsearch client <https://elasticsearch-py.readthedocs.io/>`_ when
instantiating the ``Search`` object:

.. code:: python

    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search

    client = Elasticsearch()

    s = Search(using=client)

You can also define the client at a later time (for more options see the
~:ref:`connections` chapter):

.. code:: python

    s = s.using(client)

.. note::

    All methods return a *copy* of the object, making it safe to pass to
    outside code.

The API is chainable, allowing you to combine multiple method calls in one
statement:

.. code:: python

    s = Search().using(client).query("match", title="python")

To send the request to Elasticsearch:

.. code:: python

    response = s.execute()

If you just want to iterate over the hits returned by your search you can
iterate over the ``Search`` object:

.. code:: python

    for hit in s:
        print(hit.title)

Search results will be cached. Subsequent calls to ``execute`` or trying to
iterate over an already executed ``Search`` object will not trigger additional
requests being sent to Elasticsearch. To force a request specify
``ignore_cache=True`` when calling ``execute``.

For debugging purposes you can serialize the ``Search`` object to a ``dict``
explicitly:

.. code:: python

    print(s.to_dict())

Queries
~~~~~~~


The library provides classes for all Elasticsearch query types. Pass all the
parameters as keyword arguments. The classes accept any keyword arguments, the
dsl then takes all arguments passed to the constructor and serializes them as
top-level keys in the resulting dictionary (and thus the resulting json being
sent to elasticsearch). This means that there is a clear one-to-one mapping
between the raw query and its equivalent in the DSL:

.. code:: python

    from elasticsearch_dsl.query import MultiMatch, Match

    # {"multi_match": {"query": "python django", "fields": ["title", "body"]}}
    MultiMatch(query='python django', fields=['title', 'body'])

    # {"match": {"title": {"query": "web framework", "type": "phrase"}}}
    Match(title={"query": "web framework", "type": "phrase"})

.. note::

    In some cases this approach is not possible due to python's restriction on
    identifiers - for example if your field is called ``@timestamp``. In that
    case you have to fall back to unpacking a dictionary: ``Range(**
    {'@timestamp': {'lt': 'now'}})``


You can use the ``Q`` shortcut to construct the instance using a name with
parameters or the raw ``dict``:

.. code:: python

    Q("multi_match", query='python django', fields=['title', 'body'])
    Q({"multi_match": {"query": "python django", "fields": ["title", "body"]}})

To add the query to the ``Search`` object, use the ``.query()`` method:

.. code:: python

    q = Q("multi_match", query='python django', fields=['title', 'body'])
    s = s.query(q)

The method also accepts all the parameters as the ``Q`` shortcut:

.. code:: python

    s = s.query("multi_match", query='python django', fields=['title', 'body'])

If you already have a query object, or a ``dict`` representing one, you can
just override the query used in the ``Search`` object:

.. code:: python

    s.query = Q('bool', must=[Q('match', title='python'), Q('match', body='best')])


Query combination
^^^^^^^^^^^^^^^^^

Query objects can be combined using logical operators:

.. code:: python

    Q("match", title='python') | Q("match", title='django')
    # {"bool": {"should": [...]}}

    Q("match", title='python') & Q("match", title='django')
    # {"bool": {"must": [...]}}

    ~Q("match", title="python")
    # {"bool": {"must_not": [...]}}

When you call the ``.query()`` method multiple times, the ``&`` operator will
be used internally:

.. code:: python

    s = s.query().query()
    print(s.to_dict())
    # {"query": {"bool": {...}}}

If you want to have precise control over the query form, use the ``Q`` shortcut
to directly construct the combined query:

.. code:: python

    q = Q('bool',
        must=[Q('match', title='python')],
        should=[Q(...), Q(...)],
        minimum_should_match=1
    )
    s = Search().query(q)


Filters
~~~~~~~


If you want to add a query in a `filter context
<https://www.elastic.co/guide/en/elasticsearch/reference/2.0/query-filter-context.html>`_
you can use the ``filter()`` method to make things easier:

.. code:: python

    s = Search()
    s = s.filter('terms', tags=['search', 'python'])

Behind the scenes this will produce a ``Bool`` query and place the specified
``terms`` query into its ``filter`` branch, making it equivalent to:

.. code:: python

    s = Search()
    s = s.query('bool', filter=[Q('terms', tags=['search', 'python'])])



If you want to use the post_filter element for faceted navigation, use the
``.post_filter()`` method.


Aggregations
~~~~~~~~~~~~

To define an aggregation, you can use the ``A`` shortcut:

.. code:: python

    A('terms', field='tags')
    # {"terms": {"field": "tags"}}

To nest aggregations, you can use the ``.bucket()``, ``.metric()`` and
``.pipeline()`` methods:

.. code:: python

    a = A('terms', field='category')
    # {'terms': {'field': 'category'}}

    a.metric('clicks_per_category', 'sum', field='clicks')\
        .bucket('tags_per_category', 'terms', field='tags')
    # {
    #   'terms': {'field': 'category'},
    #   'aggs': {
    #     'clicks_per_category': {'sum': {'field': 'clicks'}},
    #     'tags_per_category': {'terms': {'field': 'tags'}}
    #   }
    # }

To add aggregations to the ``Search`` object, use the ``.aggs`` property, which
acts as a top-level aggregation:

.. code:: python

    s = Search()
    a = A('terms', field='category')
    s.aggs.bucket('category_terms', a)
    # {
    #   'aggs': {
    #     'category_terms': {
    #       'terms': {
    #         'field': 'category'
    #       }
    #     }
    #   }
    # }

or

.. code:: python

    s = Search()
    s.aggs.bucket('articles_per_day', 'date_histogram', field='publish_date', interval='day')\
        .metric('clicks_per_day', 'sum', field='clicks')\
        .pipeline('moving_click_average', 'moving_avg', buckets_path='clicks_per_day')\
        .bucket('tags_per_day', 'terms', field='tags')

    s.to_dict()
    # {
    #   "aggs": {
    #     "articles_per_day": {
    #       "date_histogram": { "interval": "day", "field": "publish_date" },
    #       "aggs": {
    #         "clicks_per_day": { "sum": { "field": "clicks" } },
    #         "moving_click_average": { "moving_avg": { "buckets_path": "clicks_per_day" } },
    #         "tags_per_day": { "terms": { "field": "tags" } }
    #       }
    #     }
    #   }
    # }

You can access an existing bucket by its name:

.. code:: python

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

To specify sorting order, use the ``.sort()`` method:

.. code:: python

    s = Search().sort(
        'category',
        '-title',
        {"lines" : {"order" : "asc", "mode" : "avg"}}
    )

It accepts positional arguments which can be either strings or dictionaries.
String value is a field name, optionally prefixed by the ``-`` sign to specify
a descending order.

To reset the sorting, just call the method with no arguments:

.. code:: python

  s = s.sort()


Pagination
~~~~~~~~~~

To specify the from/size parameters, use the Python slicing API:

.. code:: python

  s = s[10:20]
  # {"from": 10, "size": 10}

If you want to access all the documents matched by your query you can use the
``scan`` method which uses the scan/scroll elasticsearch API:

.. code:: python

  for hit in s.scan():
      print(hit.title)

Note that in this case the results won't be sorted.

Highlighting
~~~~~~~~~~~~

To set common attributes for highlighting use the ``highlight_options`` method:

.. code:: python

    s = s.highlight_options(order='score')

Enabling highlighting for individual fields is done using the ``highlight`` method:

.. code:: python

    s = s.highlight('title')
    # or, including parameters:
    s = s.highlight('title', fragment_size=50)

The fragments in the response will then be available on reach ``Result`` object
as ``.meta.highlight.FIELD`` which will contain the list of fragments:

.. code:: python

    response = s.execute()
    for hit in response:
        for fragment in hit.meta.highlight.title:
            print(fragment)

Suggestions
~~~~~~~~~~~

To specify a suggest request on your ``Search`` object use the ``suggest`` method:

.. code:: python

    s = s.suggest('my_suggestion', 'pyhton', term={'field': 'title'})

The first argument is the name of the suggestions (name under which it will be
returned), second is the actual text you wish the suggester to work on and the
keyword arguments will be added to the suggest's json as-is which means that it
should be one of ``term``, ``phrase`` or ``completion`` to indicate which type
of suggester should be used.

If you only wish to run the suggestion part of the search (via the ``_suggest``
endpoint) you can do so via ``execute_suggest``:

.. code:: python

    s = s.suggest('my_suggestion', 'pyhton', term={'field': 'title'})
    suggestions = s.execute_suggest()

    print(suggestions.my_suggestion)

Extra properties and parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To set extra properties of the search request, use the ``.extra()`` method:

.. code:: python

  s = s.extra(explain=True)

To set query parameters, use the ``.params()`` method:

.. code:: python

  s = s.params(search_type="count")


If you need to limit the fields being returned by elasticsearch, use the
``fields()`` method:

.. code:: python

  # only return the selected fields
  s = s.fields(['title', 'body'])
  # reset the field selection
  s = s.fields()
  # don't return any fields, just the metadata
  s = s.fields([])

Serialization and Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The search object can be serialized into a dictionary by using the
``.to_dict()`` method.

You can also create a ``Search`` object from a ``dict`` using the ``from_dict``
class method. This will create a new ``Search`` object and populate it using
the data from the dict:

.. code:: python

  s = Search.from_dict({"query": {"match": {"title": "python"}}})

If you wish to modify an existing ``Search`` object, overriding it's
properties, instead use the ``update_from_dict`` method that alters an instance
**in-place**:

.. code:: python

  s = Search(index='i')
  s.update_from_dict({"query": {"match": {"title": "python"}}, "size": 42})

Response
--------

You can execute your search by calling the ``.execute()`` method that will return
a ``Response`` object. The ``Response`` object allows you access to any key
from the response dictionary via attribute access. It also provides some
convenient helpers:

.. code:: python

  response = s.execute()

  print(response.success())
  # True

  print(response.took)
  # 12

  print(response.hits.total)

  print(response.suggest.my_suggestions)

If you want to inspect the contents of the ``response`` objects, just use its
``to_dict`` method to get access to the raw data for pretty printing.


Hits
~~~~

To access to the hits returned by the search, access the ``hits`` property or
just iterate over the ``Response`` object:

.. code:: python

    response = s.execute()
    print('Total %d hits found.' % response.hits.total)
    for h in response:
        print(h.title, h.body)


Result
~~~~~~

The individual hits is wrapped in a convenience class that allows attribute
access to the keys in the returned dictionary. All the metadata for the results
are accessible via ``meta`` (without the leading ``_``):

.. code:: python

    response = s.execute()
    h = response.hits[0]
    print('/%s/%s/%s returned with score %f' % (
        h.meta.index, h.meta.doc_type, h.meta.id, h.meta.score))

.. note::

    If your document has a field called ``meta`` you have to access it using
    the get item syntax: ``hit['meta']``.


Aggregations
~~~~~~~~~~~~

Aggregations are available through the ``aggregations`` property:

.. code:: python

    for tag in response.aggregations.per_tag.buckets:
        print(tag.key, tag.max_lines.value)



``MultiSearch``
---------------

If you need to execute multiple searches at the same time you can use the
``MultiSearch`` class which will use the ``_msearch`` API:

.. code:: python

    from elasticsearch_dsl import MultiSearch, Search

    ms = MultiSearch(index='blogs')

    ms = ms.add(Search().filter('term', tags='python'))
    ms = ms.add(Search().filter('term', tags='elasticsearch'))

    responses = ms.execute()

    for response in responses:
        print("Results for query %r." % response.search.query)
        for hit in response:
            print(hit.title)
