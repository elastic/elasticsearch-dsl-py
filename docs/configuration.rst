Configuration
=============

Connections for the library can be configured several ways using the
``connections`` module. Defining one default global connection is easy and
useful since API calls can be made every time without explicitly passing
in another connection.

A default global connection is generally preferred. When additional
flexibility is needed, manual connections and multiple connections to multiple
clusters may also be configured.

When using ``elasticsearch_dsl`` it is highly recommended to use the attached
serializer (``elasticsearch_dsl.serializer.serializer``) that will make sure
your objects are correctly serialized into json every time. The
``create_connection`` method that is described here (and that ``configure``
method uses under the hood) will do that automatically for you, unless you
explicitly specify your own serializer.

.. note::

    Unless you want to access multiple clusters from your application it is
    highly recommended that you use the ``create_connection`` method and all
    operations will use that connection automatically.

.. _default-global-connection:

Default global connection
-------------------------

To define a default connection that will be used globally, use the
``connections`` module and its ``create_connection`` method:

.. code:: python

    from elasticsearch_dsl import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

Any keyword arguments (``hosts`` and ``timeout`` in our example) will be passed
by the ``create_connection`` method to the ``Elasticsearch`` class.

Manual connection
-----------------

If you don't wish to use the default global connection you can always configure
a manual connection with the ``create_connection`` method. The manual
connection may be passed to other methods by using the keyword ``using`` and
the value of the connection (instance of ``elasticsearch.Elasticsearch``):

.. code:: python

    s = Search(using=Elasticsearch('localhost'))

You can even use this approach to override any connection the object might be
already associated with:

.. code:: python

    s = s.using(Elasticsearch('otherhost:9200')

An example:

.. code:: python

    from elasticsearch_dsl import connections

    // Create manual configured connection
    local_connection = connections.create_connection(hosts=['localhost'], timeout=20)

    s = Search(using=Elasticsearch('localhost'))
    ...

    // Create a connection to otherhost
    s = s.using(Elasticsearch('otherhost:9200')
    ...

    // Set connection back to localhost
    s = s.using(Elasticsearch(local_connection))

Multiple clusters
-----------------

Multiple connections to multiple clusters may be created. Create multiple
connections at the same time using the ``configure`` method:

.. code:: python

    from elasticsearch_dsl import connections

    connections.configure(
        default={'hosts': 'localhost'},
        dev={'hosts': ['esdev1.example.com:9200'], sniff_on_start=True}
    )

Connections will be constructed lazily when requested for the first time.

Or just add the multiple connections one by one:

.. code:: python

    # if you have configuration to be passed to Elasticsearch.__init__
    connections.create_connection('qa', hosts=['esqa1.example.com'], sniff_on_start=True)

    # if you already have an Elasticsearch instance ready
    connections.add_connection('qa', my_client)

Using aliases
~~~~~~~~~~~~~

Aliases are handy when working with multiple connections. Using multiple
connections you can just refer to a connection using the string
alias you registered it under:

.. code:: python

    s = Search(using='qa')

``KeyError`` will be raised if the alias does not have a connection registered.
