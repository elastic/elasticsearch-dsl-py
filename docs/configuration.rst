Configuration
=============

There are several ways how to configure connections for the library. Easiest
option, and most useful, is to just define one default connection that will be
used every time an API call is made without explicitly passing in other
connection.

When using ``elasticsearch_dsl`` it is highly recommended to use the attached
serializer (``elasticsearch_dsl.serializer.serializer``) that will make sure
your objects are correctly serialized into json every time. The
``create_connection`` method that is described here (and that ``configure``
method uses under the hood) will do that automatically for you, unless you
explicitly specify your own serializer. The serializer we use will also allow
you to serialize your own objects - just define a ``to_dict()`` method on your
objects and it will automatically be called when serializing to json.

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

    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

Any keyword arguments (``hosts`` and ``timeout`` in our example) will be passed
to the ``Elasticsearch`` class.

Multiple clusters
-----------------

You can define multiple connections to multiple clusters, either at the same
time using the ``configure`` method:

.. code:: python

    from elasticsearch_dsl.connections import connections

    connections.configure(
        default={'hosts': 'localhost'},
        dev={'hosts': ['esdev1.example.com:9200'], sniff_on_start=True}
    )

Such connections will be constructed lazily when requested for the first time.

Or just add them one by one:

.. code:: python

    # if you have configuration to be passed to Elasticsearch.__init__
    connections.create_connection('qa', hosts=['esqa1.example.com'], sniff_on_start=True)

    # if you already have an Elasticsearch instance ready
    connections.add_connection('qa', my_client)

Using aliases
~~~~~~~~~~~~~

When using multiple connections you can just refer to them using the string
alias you registered them under:

.. code:: python

    s = Search(using='qa')

``KeyError`` will be raised if there is no connection registered under that
alias.

