Configuration
=============

There are several ways how to configure connections for the library. Easiest
option, and most useful, is to just define one default connection that will be
used every time an API call is made without explicitly passing in other
connection.

.. note::

    Unless you want to access multiple clusters from your application it is
    highly recommended that you use the ``create_connection`` method and all
    operations will use that connection automatically.


Manual
------

If you don't wish to supply global configuration you can always pass in your
own connection (instance of ``elasticsearch.Elasticsearch``) as parameter
``using`` wherever it is accepted:

.. code:: python

    s = Search(using=Elasticsearch('localhost'))

You can even use this approach to override any connection the object might be
already associated with:

.. code:: python

    s = s.using(Elasticsearch('otherhost:9200')


.. _default connection:

Default connection
------------------

To define a default connection that will be used globally, use the
``connections`` module and the ``create_connection`` method:

.. code:: python

    from elasticsearch_dsl import connections

    connections.connections.create_connection(hosts=['localhost'], timeout=20)

Any keyword arguments (``hosts`` and ``timeout`` in our example) will be passed
to the ``Elasticsearch`` class.

Multiple clusters
-----------------

You can define multiple connections to multiple clusters, either at the same
time using the ``configure`` method:

.. code:: python

    from elasticsearch_dsl import connections

    connections.configure(
        default={'hosts': 'localhost'},
        dev={'hosts': ['esdev1.example.com:9200'], sniff_on_start=True}
    )

Such connections will be constructed lazily when requested for the first time.

Or just add them one by one:

.. code:: python

    connections.add_connection('qa', hosts=['esqa1.example.com'], sniff_on_start=True)

Using aliases
~~~~~~~~~~~~~

When using multiple connections you can just refer to them using the string
alias you registered them under:

.. code:: python

    s = Search(using='qa')

``KeyError`` will be raised if there is no connection registered under that
alias.

