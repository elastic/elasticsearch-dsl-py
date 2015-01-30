.. _changelog:

Changelog
=========

0.0.4 (dev)
-----------

 * only document id can now be set directly on a document. Rest of the metadata
   fields (such as index, version etc) must be stored (and retrieved) using the
   ``_meta`` attribute (#58)
 * query on Search can now be directly assigned
 * ``suggest`` method added to ``Search``
 * ``Search.doc_type`` now accepts ``DocType`` subclasses directly

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
