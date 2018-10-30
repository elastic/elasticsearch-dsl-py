.. _api:

API Documentation
=================

Below please find the documentation for the public classes and functions of ``elasticsearch_dsl``.

.. py:module:: elasticsearch_dsl

Search
------

.. autoclass:: Search
   :members:

.. autoclass:: MultiSearch
   :members:

Document
--------

.. autoclass:: Document
   :members:

Index
-----

.. autoclass:: Index
   :members:

Faceted Search
--------------

.. autoclass:: FacetedSearch
   :members:

Update By Query 
----------------
.. autoclass:: UpdateByQuery
  :members:

Mappings
--------

If you wish to create mappings manually you can use the ``Mapping`` class, for
more advanced use cases, however, we recommend you use the :ref:`doc_type`
abstraction in combination with :ref:`index` (or :ref:`index-template`) to define
index-level settings and properties. The mapping definition follows a similar
pattern to the query dsl:

.. code:: python

    from elasticsearch_dsl import Keyword, Mapping, Nested, Text

    # name your type
    m = Mapping('my-type')

    # add fields
    m.field('title', 'text')

    # you can use multi-fields easily
    m.field('category', 'text', fields={'raw': Keyword()})

    # you can also create a field manually
    comment = Nested(
                     properties={
                        'author': Text(),
                        'created_at': Date()
                     })

    # and attach it to the mapping
    m.field('comments', comment)

    # you can also define mappings for the meta fields
    m.meta('_all', enabled=False)

    # save the mapping into index 'my-index'
    m.save('my-index')

.. note::

    By default all fields (with the exception of ``Nested``) will expect single
    values. You can always override this expectation during the field
    creation/definition by passing in ``multi=True`` into the constructor
    (``m.field('tags', Keyword(multi=True))``). Then the
    value of the field, even if the field hasn't been set, will be an empty
    list enabling you to write ``doc.tags.append('search')``.

Especially if you are using dynamic mappings it might be useful to update the
mapping based on an existing type in Elasticsearch, or create the mapping
directly from an existing type:

.. code:: python

    # get the mapping from our production cluster
    m = Mapping.from_es('my-index', 'my-type', using='prod')

    # update based on data in QA cluster
    m.update_from_es('my-index', using='qa')

    # update the mapping on production
    m.save('my-index', using='prod')

Common field options:

``multi``
  If set to ``True`` the field's value will be set to ``[]`` at first access.

``required``
  Indicates if a field requires a value for the document to be valid.


