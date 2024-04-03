.. _asyncio:

Using asyncio with Elasticsearch DSL
====================================

The ``elasticsearch-dsl`` package supports async/await with `asyncio <https://docs.python.org/3/library/asyncio.html>`__.
To ensure that you have all the required dependencies, install the ``[async]`` extra:

   .. code:: bash

       $ python -m pip install elasticsearch-dsl[async]

Connections
-----------

Use the ``async_connections`` module to manage your asynchronous connections.

   .. code:: python

       from elasticsearch_dsl import async_connections

       async_connections.create_connection(hosts=['localhost'], timeout=20)

All the options available in the ``connections`` module can be used with ``async_connections``.

How to avoid 'Unclosed client session / connector' warnings on exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These warnings come from the ``aiohttp`` package, which is used internally by the
``AsyncElasticsearch`` client. They appear often when the application exits and
are caused by HTTP connections that are open when they are garbage collected. To
avoid these warnings, make sure that you close your connections.

   .. code:: python

       es = async_connections.get_connection()
       await es.close()

Search DSL
----------

Use the ``AsyncSearch`` class to perform asynchronous searches.

   .. code:: python

       from elasticsearch_dsl import AsyncSearch

       s = AsyncSearch().query("match", title="python")
       async for hit in s:
           print(hit.title)

Instead of using the ``AsyncSearch`` object as an asynchronous iterator, you can
explicitly call the ``execute()`` method to get a ``Response`` object.

    .. code:: python

       s = AsyncSearch().query("match", title="python")
       response = await s.execute()
       for hit in response:
           print(hit.title)
 
An ``AsyncMultiSearch`` is available as well.

   .. code:: python

       from elasticsearch_dsl import AsyncMultiSearch

       ms = AsyncMultiSearch(index='blogs')

       ms = ms.add(AsyncSearch().filter('term', tags='python'))
       ms = ms.add(AsyncSearch().filter('term', tags='elasticsearch'))

       responses = await ms.execute()

       for response in responses:
           print("Results for query %r." % response.search.query)
           for hit in response:
               print(hit.title)

Asynchronous Documents, Indexes, and more
-----------------------------------------

The ``Document``, ``Index``, ``IndexTemplate``, ``Mapping``, ``UpdateByQuery`` and
``FacetedSearch`` classes all have asynchronous versions that use the same name
with an ``Async`` prefix. These classes expose the same interfaces as the
synchronous versions, but any methods that perform I/O are defined as coroutines.

Auxiliary classes that do not perform I/O do not have asynchronous versions. The
same classes can be used in synchronous and asynchronous applications.

When using a :ref:`custom analyzer <Analysis>` in an asynchronous application, use
the ``async_simulate()`` method to invoke the Analyze API on it.

Consult the :ref:`api` section for details about each specific method.
