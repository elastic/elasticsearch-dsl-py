.. _api:

API Documentation
=================

Below please find the documentation for the public classes and functions of ``elasticsearch_dsl``.

.. py:module:: elasticsearch_dsl

Query
-----

.. autofunction:: Q

Aggs
----

.. autofunction:: A

Function
--------

.. autofunction:: SF

Search
------

.. autoclass:: Search
   :members:

.. autoclass:: MultiSearch
   :members:

Field
-----

``elasticsearch_dsl`` implements a number of different ``fields`` which can be
contained within ``documents``. All of these fields subclass ``Field``.

.. autoclass:: Field
   :members:

.. autofunction:: construct_field

.. autoclass:: Object
   :members:

.. autoclass:: Nested
   :members:

.. autoclass:: Date
   :members:

.. autoclass:: String
   :members:

.. autoclass:: Float
   :members:

.. autoclass:: Double
   :members:

.. autoclass:: Byte
   :members:

.. autoclass:: Short
   :members:

.. autoclass:: Integer
   :members:

.. autoclass:: Long
   :members:

.. autoclass:: Boolean
   :members:

.. autoclass:: Ip
   :members:

.. autoclass:: Attachment
   :members:

.. autoclass:: GeoPoint
   :members:

.. autoclass:: GeoShape
   :members:

.. autoclass:: InnerObjectWrapper
   :members:

.. autoclass:: Keyword
   :members:

.. autoclass:: Text
   :members:

Document
--------

.. autoclass:: DocType
   :members:

Mapping
-------

.. autoclass:: Mapping
   :members:

Index
-----

.. autoclass:: Index
   :members:

Analysis
--------

.. autoclass:: tokenizer
   :members:

.. autoclass:: analyzer
   :members:

.. autoclass:: char_filter
   :members:

.. autoclass:: token_filter
   :members:

Faceted Search
--------------

.. autoclass:: FacetedSearch
   :members:

.. autoclass:: HistogramFacet
   :members:

.. autoclass:: TermsFacet
   :members:

.. autoclass:: DateHistogramFacet
   :members:

.. autoclass:: RangeFacet
   :members:
