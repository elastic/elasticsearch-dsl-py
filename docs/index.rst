Elasticsearch DSL
=================

Elasticsearch DSL is a high-level library whose aim is to help with writing and
running queries against Elasticsearch. It is built on top of the official
low-level client (`elasticsearch-py <https://github.com/elastic/elasticsearch-py>`_).

It provides a more convenient and idiomatic way to write and manipulate
queries. It stays close to the Elasticsearch JSON DSL, mirroring its
terminology and structure. It exposes the whole range of the DSL from Python
either directly using defined classes or a queryset-like expressions. Here is
an example::

    from elasticsearch_dsl import Search

    s = Search(index="my-index") \
        .filter("term", category="search") \
        .query("match", title="python")   \
        .exclude("match", description="beta")
    for hit in s:
        print(hit.title)

Or with asynchronous Python::

    from elasticsearch_dsl import AsyncSearch

    async def run_query():
        s = AsyncSearch(index="my-index") \
            .filter("term", category="search") \
            .query("match", title="python")   \
            .exclude("match", description="beta")
        async for hit in s:
            print(hit.title)

It also provides an optional wrapper for working with documents as Python
objects: defining mappings, retrieving and saving documents, wrapping the
document data in user-defined classes.

To use the other Elasticsearch APIs (eg. cluster health) just use the
underlying client.

Installation
------------

Install the ``elasticsearch-dsl`` package with `pip <https://pypi.org/project/elasticsearch>`_::

  pip install elasticsearch-dsl

For asynchronous applications, install with the ``async`` extra::

  pip install elasticsearch-dsl[async]

Read more about :ref:`how to use asyncio with this project <asyncio>`.

Examples
--------

Please see the `examples
<https://github.com/elastic/elasticsearch-dsl-py/tree/master/examples>`_
directory to see some complex examples using ``elasticsearch-dsl``.

Compatibility
-------------

The library is compatible with all Elasticsearch versions since ``2.x`` but you
**have to use a matching major version**:

For **Elasticsearch 8.0** and later, use the major version 8 (``8.x.y``) of the
library.

For **Elasticsearch 7.0** and later, use the major version 7 (``7.x.y``) of the
library.

For **Elasticsearch 6.0** and later, use the major version 6 (``6.x.y``) of the
library.

For **Elasticsearch 5.0** and later, use the major version 5 (``5.x.y``) of the
library.

For **Elasticsearch 2.0** and later, use the major version 2 (``2.x.y``) of the
library.

The recommended way to set your requirements in your `setup.py` or
`requirements.txt` is::

    # Elasticsearch 8.x
    elasticsearch-dsl>=8.0.0,<9.0.0

    # Elasticsearch 7.x
    elasticsearch-dsl>=7.0.0,<8.0.0

    # Elasticsearch 6.x
    elasticsearch-dsl>=6.0.0,<7.0.0

    # Elasticsearch 5.x
    elasticsearch-dsl>=5.0.0,<6.0.0

    # Elasticsearch 2.x
    elasticsearch-dsl>=2.0.0,<3.0.0


The development is happening on ``main``, older branches only get bugfix releases

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
   :caption: About
   :maxdepth: 2

   self
   configuration

.. toctree::
   :caption: Tutorials
   :maxdepth: 2

   tutorials

.. toctree::
   :caption: How-To Guides
   :maxdepth: 2

   search_dsl
   persistence
   faceted_search
   update_by_query
   asyncio

.. toctree::
   :caption: Reference
   :maxdepth: 2

   api
   async_api

.. toctree::
   :caption: Community
   :maxdepth: 2

   CONTRIBUTING
   Changelog
