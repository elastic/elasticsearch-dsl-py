.. _changelog:

Changelog
=========

2.0.0 (2016-02-18)
------------------
Compatibility with Eelasticsearch 2.x:

 * Filters have been removed and additional queries have been added
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
