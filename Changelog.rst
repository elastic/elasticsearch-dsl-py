.. _changelog:

Changelog
=========

master
------
 * fix bug in loading an aggregation with meta data from dict

5.3.0 (2017-05-18)
------------------
 * fix constant score query definition
 * ``DateHistogramFacet`` now works with ``datetime`` objects
 * respect ``__`` in field names when creating queries from dict

5.2.0 (2017-03-26)
------------------
 * make sure all response structers are pickleable (for caching)
 * adding ``exclude`` to ``Search``
 * fix metric aggregation deserialization
 * expose all index-level APIs on ``Index`` class
 * adding ``delete`` to ``Search`` which calls ``delete_by_query`` API

5.1.0 (2017-01-08)
------------------
 * Renamed ``Result`` and ``ResultMeta`` to ``Hit`` and ``HitMeta`` respectively
 * ``Response`` now stores ``Search`` which it gets as first arg to ``__init__``
 * aggregation results are now wrapped in classes and properly deserialized
 * ``Date`` fields now allow for numerical timestamps in the java format (in millis)
 * Added API documentation
 * replaced generated classes with manually created

5.0.0 (2016-11-04)
------------------
Version compatible with elasticsearch 5.0.

Breaking changes:

 * ``String`` field type has been deprecated in favor of ``Text`` and ``Keyword``
 * ``fields`` method has been removed in favor of ``source`` filtering

2.2.0 (2016-11-04)
------------------
 * accessing missing string fields no longer returnd ``''`` but returns
   ``None`` instead.
 * fix issues with bool's ``|`` and ``&`` operators and ``minimum_should_match``

2.1.0 (2016-06-29)
------------------
 * ``inner_hits`` are now also wrapped in ``Response``
 * ``+`` operator is deprecated, ``.query()`` now uses ``&`` to combine queries
 * added ``mget`` method to ``DocType``
 * fixed validation for "empty" values like ``''`` and ``[]``

2.0.0 (2016-02-18)
------------------
Compatibility with Elasticsearch 2.x:

 * Filters have been removed and additional queries have been added. Instead of
   ``F`` objects you can now use ``Q``.
 * ``Search.filter`` is now just a shortcut to add queries in filter context
 * support for pipeline aggregations added

Backwards incompatible changes:

 * list of analysis objects and classes was removed, any string used as
   tokenizer, char or token filter or analyzer will be treated as a builtin
 * internal method ``Field.to_python`` has been renamed to ``deserialize`` and
   an optional serialization mechanic for fields has been added.
 * Custom response class is now set by ``response_class`` method instead of a
   kwarg to ``Search.execute``

Other changes:

 * ``FacetedSearch`` now supports pagination via slicing

0.0.10 (2016-01-24)
-------------------
 * ``Search`` can now be iterated over to get back hits
 * ``Search`` now caches responses from Elasticsearch
 * ``DateHistogramFacet`` now defaults to returning empty intervals
 * ``Search`` no longer accepts positional parameters
 * Experimental ``MultiSearch`` API
 * added option to talk to ``_suggest`` endpoint (``execute_suggest``)

0.0.9 (2015-10-26)
------------------
 * ``FacetedSearch`` now uses its own ``Facet`` class instead of built in
   aggregations

0.0.8 (2015-08-28)
------------------
 * ``0.0.5`` and ``0.0.6`` was released with broken .tar.gz on pypi, just a build fix

0.0.5 (2015-08-27)
------------------
 * added support for (index/search)_analyzer via #143, thanks @wkiser!
 * even keys accessed via ``['field']`` on ``AttrDict`` will be wrapped in
   ``Attr[Dict|List]`` for consistency
 * Added a convenient option to specify a custom ``doc_class`` to wrap
   inner/Nested documents
 * ``blank`` option has been removed
 * ``AttributeError`` is no longer raised when accessing an empty field.
 * added ``required`` flag to fields and validation hooks to fields and
   (sub)documents
 * removed ``get`` method from ``AttrDict``. Use ``getattr(d, key, default)``
   instead.
 * added ``FacetedSearch`` for easy declarative faceted navigation

0.0.4 (2015-04-24)
------------------

 * Metadata fields (such as id, parent, index, version etc) must be stored (and
   retrieved) using the ``meta`` attribute (#58) on both ``Result`` and
   ``DocType`` objects or using their underscored variants (``_id``,
   ``_parent`` etc)
 * query on Search can now be directly assigned
 * ``suggest`` method added to ``Search``
 * ``Search.doc_type`` now accepts ``DocType`` subclasses directly
 * ``Properties.property`` method renamed to ``field`` for consistency
 * Date field now raises ``ValidationException`` on incorrect data

0.0.3 (2015-01-23)
------------------

Added persistence layer (``Mapping`` and ``DocType``), various fixes and
improvements.

0.0.2 (2014-08-27)
------------------

Fix for python 2

0.0.1 (2014-08-27)
------------------

Initial release.
