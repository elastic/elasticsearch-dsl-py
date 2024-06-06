.. _persistence:

Persistence
===========

You can use the dsl library to define your mappings and a basic persistent
layer for your application.

For more comprehensive examples have a look at the examples_ directory in the
repository.

.. _examples: https://github.com/elastic/elasticsearch-dsl-py/tree/master/examples

.. _doc_type:

Document
--------

If you want to create a model-like wrapper around your documents, use the
``Document`` class. It can also be used to create all the necessary mappings and
settings in elasticsearch (see :ref:`life-cycle` for details).

.. code:: python

    from datetime import datetime
    from elasticsearch_dsl import Document, Date, Nested, Boolean, \
        analyzer, InnerDoc, Completion, Keyword, Text

    html_strip = analyzer('html_strip',
        tokenizer="standard",
        filter=["standard", "lowercase", "stop", "snowball"],
        char_filter=["html_strip"]
    )

    class Comment(InnerDoc):
        author = Text(fields={'raw': Keyword()})
        content = Text(analyzer='snowball')
        created_at = Date()

        def age(self):
            return datetime.now() - self.created_at

    class Post(Document):
        title = Text()
        title_suggest = Completion()
        created_at = Date()
        published = Boolean()
        category = Text(
            analyzer=html_strip,
            fields={'raw': Keyword()}
        )

        comments = Nested(Comment)

        class Index:
            name = 'blog'

        def add_comment(self, author, content):
            self.comments.append(
              Comment(author=author, content=content, created_at=datetime.now()))

        def save(self, ** kwargs):
            self.created_at = datetime.now()
            return super().save(** kwargs)

Data types
~~~~~~~~~~

The ``Document`` instances should be using native python types like
``datetime``. In case of ``Object`` or ``Nested`` fields an instance of the
``InnerDoc`` subclass should be used just like in the ``add_comment`` method in
the above example where we are creating an instance of the ``Comment`` class.

There are some specific types that were created as part of this library to make
working with specific field types easier, for example the ``Range`` object used
in any of the `range fields
<https://www.elastic.co/guide/en/elasticsearch/reference/current/range.html>`_:

.. code:: python

    from elasticsearch_dsl import Document, DateRange, Keyword, Range

    class RoomBooking(Document):
        room = Keyword()
        dates = DateRange()


    rb = RoomBooking(
      room='Conference Room II',
      dates=Range(
        gte=datetime(2018, 11, 17, 9, 0, 0),
        lt=datetime(2018, 11, 17, 10, 0, 0)
      )
    )

    # Range supports the in operator correctly:
    datetime(2018, 11, 17, 9, 30, 0) in rb.dates # True

    # you can also get the limits and whether they are inclusive or exclusive:
    rb.dates.lower # datetime(2018, 11, 17, 9, 0, 0), True
    rb.dates.upper # datetime(2018, 11, 17, 10, 0, 0), False

    # empty range is unbounded
    Range().lower # None, False

Note on dates
~~~~~~~~~~~~~

``elasticsearch-dsl`` will always respect the timezone information (or lack
thereof) on the ``datetime`` objects passed in or stored in Elasticsearch.
Elasticsearch itself interprets all datetimes with no timezone information as
``UTC``. If you wish to reflect this in your python code, you can specify
``default_timezone`` when instantiating a ``Date`` field:

.. code:: python

    class Post(Document):
        created_at = Date(default_timezone='UTC')

In that case any ``datetime`` object passed in (or parsed from elasticsearch)
will be treated as if it were in ``UTC`` timezone.

.. _life-cycle:

Document life cycle
~~~~~~~~~~~~~~~~~~~

Before you first use the ``Post`` document type, you need to create the
mappings in Elasticsearch. For that you can either use the :ref:`index` object
or create the mappings directly by calling the ``init`` class method:

.. code:: python

    # create the mappings in Elasticsearch
    Post.init()

This code will typically be run in the setup for your application during a code
deploy, similar to running database migrations.

To create a new ``Post`` document just instantiate the class and pass in any
fields you wish to set, you can then use standard attribute setting to
change/add more fields. Note that you are not limited to the fields defined
explicitly:

.. code:: python

    # instantiate the document
    first = Post(title='My First Blog Post, yay!', published=True)
    # assign some field values, can be values or lists of values
    first.category = ['everything', 'nothing']
    # every document has an id in meta
    first.meta.id = 47


    # save the document into the cluster
    first.save()


All the metadata fields (``id``, ``routing``, ``index`` etc) can be
accessed (and set) via a ``meta`` attribute or directly using the underscored
variant:

.. code:: python

    post = Post(meta={'id': 42})

    # prints 42
    print(post.meta.id)

    # override default index
    post.meta.index = 'my-blog'

.. note::

    Having all metadata accessible through ``meta`` means that this name is
    reserved and you shouldn't have a field called ``meta`` on your document.
    If you, however, need it you can still access the data using the get item
    (as opposed to attribute) syntax: ``post['meta']``.

To retrieve an existing document use the ``get`` class method:

.. code:: python

    # retrieve the document
    first = Post.get(id=42)
    # now we can call methods, change fields, ...
    first.add_comment('me', 'This is nice!')
    # and save the changes into the cluster again
    first.save()

The `Update API
<https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-update.html>`_
can also be used via the ``update`` method. By default any keyword arguments,
beyond the parameters of the API, will be considered fields with new values.
Those fields will be updated on the local copy of the document and then sent
over as partial document to be updated:

.. code:: python

    # retrieve the document
    first = Post.get(id=42)
    # you can update just individual fields which will call the update API
    # and also update the document in place
    first.update(published=True, published_by='me')

In case you wish to use a ``painless`` script to perform the update you can
pass in the script string as ``script`` or the ``id`` of a `stored script
<https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-scripting-using.html#modules-scripting-stored-scripts>`_
via ``script_id``. All additional keyword arguments to the ``update`` method
will then be passed in as parameters of the script. The document will not be
updated in place.

.. code:: python

    # retrieve the document
    first = Post.get(id=42)
    # we execute a script in elasticsearch with additional kwargs being passed
    # as params into the script
    first.update(script='ctx._source.category.add(params.new_category)',
                 new_category='testing')

If the document is not found in elasticsearch an exception
(``elasticsearch.NotFoundError``) will be raised. If you wish to return
``None`` instead just pass in ``ignore=404`` to suppress the exception:

.. code:: python

    p = Post.get(id='not-in-es', ignore=404)
    p is None

When you wish to retrieve multiple documents at the same time by their ``id``
you can use the ``mget`` method:

.. code:: python

    posts = Post.mget([42, 47, 256])

``mget`` will, by default, raise a ``NotFoundError`` if any of the documents
wasn't found and ``RequestError`` if any of the document had resulted in error.
You can control this behavior by setting parameters:

``raise_on_error``
  If ``True`` (default) then any error will cause an exception to be raised.
  Otherwise all documents containing errors will be treated as missing.

``missing``
  Can have three possible values: ``'none'`` (default), ``'raise'`` and
  ``'skip'``. If a document is missing or errored it will either be replaced
  with ``None``, an exception will be raised or the document will be skipped in
  the output list entirely.


The index associated with the ``Document`` is accessible via the ``_index``
class property which gives you access to the :ref:`index` class.

The ``_index`` attribute is also home to the ``load_mappings`` method which will
update the mapping on the ``Index`` from elasticsearch. This is very useful
if you use dynamic mappings and want the class to be aware of those fields (for
example if you wish the ``Date`` fields to be properly (de)serialized):

.. code:: python

    Post._index.load_mappings()

To delete a document just call its ``delete`` method:

.. code:: python

    first = Post.get(id=42)
    first.delete()

.. _analysis:

Analysis
~~~~~~~~

To specify ``analyzer`` values for ``Text`` fields you can just use the name
of the analyzer (as a string) and either rely on the analyzer being defined
(like built-in analyzers) or define the analyzer yourself manually.

Alternatively you can create your own analyzer and have the persistence layer
handle its creation, from our example earlier:

.. code:: python

    from elasticsearch_dsl import analyzer, tokenizer

    my_analyzer = analyzer('my_analyzer',
        tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
        filter=['lowercase']
    )

Each analysis object needs to have a name (``my_analyzer`` and ``trigram`` in
our example) and tokenizers, token filters and char filters also need to
specify type (``nGram`` in our example).

Once you have an instance of a custom ``analyzer`` you can also call the
`analyze API
<https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-analyze.html>`_
on it by using the ``simulate`` method:

.. code:: python

    response = my_analyzer.simulate('Hello World!')

    # ['hel', 'ell', 'llo', 'lo ', 'o w', ' wo', 'wor', 'orl', 'rld', 'ld!']
    tokens = [t.token for t in response.tokens]

.. note::

    When creating a mapping which relies on a custom analyzer the index must
    either not exist or be closed. To create multiple ``Document``-defined
    mappings you can use the :ref:`index` object.

Search
~~~~~~

To search for this document type, use the ``search`` class method:

.. code:: python

    # by calling .search we get back a standard Search object
    s = Post.search()
    # the search is already limited to the index and doc_type of our document
    s = s.filter('term', published=True).query('match', title='first')


    results = s.execute()

    # when you execute the search the results are wrapped in your document class (Post)
    for post in results:
        print(post.meta.score, post.title)

Alternatively you can just take a ``Search`` object and restrict it to return
our document type, wrapped in correct class:

.. code:: python

    s = Search()
    s = s.doc_type(Post)

You can also combine document classes with standard doc types (just strings),
which will be treated as before. You can also pass in multiple ``Document``
subclasses and each document in the response will be wrapped in it's class.

If you want to run suggestions, just use the ``suggest`` method on the
``Search`` object:

.. code:: python

    s = Post.search()
    s = s.suggest('title_suggestions', 'pyth', completion={'field': 'title_suggest'})

    response = s.execute()

    for result in response.suggest.title_suggestions:
        print('Suggestions for %s:' % result.text)
        for option in result.options:
            print('  %s (%r)' % (option.text, option.payload))


``class Meta`` options
~~~~~~~~~~~~~~~~~~~~~~

In the ``Meta`` class inside your document definition you can define various
metadata for your document:

``mapping``
  optional instance of ``Mapping`` class to use as base for the mappings
  created from the fields on the document class itself.

Any attributes on the ``Meta`` class that are instance of ``MetaField`` will be
used to control the mapping of the meta fields (``_all``, ``dynamic`` etc).
Just name the parameter (without the leading underscore) as the field you wish
to map and pass any parameters to the ``MetaField`` class:

.. code:: python

    class Post(Document):
        title = Text()

        class Meta:
            all = MetaField(enabled=False)
            dynamic = MetaField('strict')

``class Index`` options
~~~~~~~~~~~~~~~~~~~~~~~

This section of the ``Document`` definition can contain any information about
the index, its name, settings and other attributes:

``name``
  name of the index to use, if it contains a wildcard (``*``) then it cannot be
  used for any write operations and an ``index`` kwarg will have to be passed
  explicitly when calling methods like ``.save()``.

``using``
  default connection alias to use, defaults to ``'default'``

``settings``
  dictionary containing any settings for the ``Index`` object like
  ``number_of_shards``.

``analyzers``
  additional list of analyzers that should be defined on an index (see
  :ref:`analysis` for details).

``aliases``
  dictionary with any aliases definitions

Document Inheritance
~~~~~~~~~~~~~~~~~~~~

You can use standard Python inheritance to extend models, this can be useful in
a few scenarios. For example if you want to have a ``BaseDocument`` defining
some common fields that several different ``Document`` classes should share:

.. code:: python

    class User(InnerDoc):
        username = Text(fields={'keyword': Keyword()})
        email = Text()

    class BaseDocument(Document):
        created_by = Object(User)
        created_date = Date()
        last_updated = Date()

        def save(**kwargs):
            if not self.created_date:
                self.created_date = datetime.now()
            self.last_updated = datetime.now()
            return super(BaseDocument, self).save(**kwargs)

    class BlogPost(BaseDocument):
        class Index:
            name = 'blog'

Another use case would be using the `join type
<https://www.elastic.co/guide/en/elasticsearch/reference/current/parent-join.html>`_
to have multiple different entities in a single index. You can see an `example
<https://github.com/elastic/elasticsearch-dsl-py/blob/master/examples/parent_child.py>`_
of this approach. Note that in this case, if the subclasses don't define their
own `Index` classes, the mappings are merged and shared between all the
subclasses.

.. _index:

Index
-----

In typical scenario using ``class Index`` on a ``Document`` class is sufficient
to perform any action. In a few cases though it can be useful to manipulate an
``Index`` object directly.

``Index`` is a class responsible for holding all the metadata related to an
index in elasticsearch - mappings and settings. It is most useful when defining
your mappings since it allows for easy creation of multiple mappings at the
same time. This is especially useful when setting up your elasticsearch objects
in a migration:

.. code:: python

    from elasticsearch_dsl import Index, Document, Text, analyzer

    blogs = Index('blogs')

    # define custom settings
    blogs.settings(
        number_of_shards=1,
        number_of_replicas=0
    )

    # define aliases
    blogs.aliases(
        old_blogs={}
    )

    # register a document with the index
    blogs.document(Post)

    # can also be used as class decorator when defining the Document
    @blogs.document
    class Post(Document):
        title = Text()

    # You can attach custom analyzers to the index

    html_strip = analyzer('html_strip',
        tokenizer="standard",
        filter=["standard", "lowercase", "stop", "snowball"],
        char_filter=["html_strip"]
    )

    blogs.analyzer(html_strip)

    # delete the index, ignore if it doesn't exist
    blogs.delete(ignore=404)

    # create the index in elasticsearch
    blogs.create()

You can also set up a template for your indices and use the ``clone`` method to
create specific copies:

.. code:: python

    blogs = Index('blogs', using='production')
    blogs.settings(number_of_shards=2)
    blogs.document(Post)

    # create a copy of the index with different name
    company_blogs = blogs.clone('company-blogs')

    # create a different copy on different cluster
    dev_blogs = blogs.clone('blogs', using='dev')
    # and change its settings
    dev_blogs.setting(number_of_shards=1)

.. _index-template:

IndexTemplate
~~~~~~~~~~~~~

``elasticsearch-dsl`` also exposes an option to manage `index templates
<https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html>`_
in elasticsearch using the ``IndexTemplate`` class which has very similar API to ``Index``.


Once an index template is saved in elasticsearch it's contents will be
automatically applied to new indices (existing indices are completely
unaffected by templates) that match the template pattern (any index starting
with ``blogs-`` in our example), even if the index is created automatically
upon indexing a document into that index.

Potential workflow for a set of time based indices governed by a single template:

.. code:: python

    from datetime import datetime

    from elasticsearch_dsl import Document, Date, Text


    class Log(Document):
        content = Text()
        timestamp = Date()

        class Index:
            name = "logs-*"
            settings = {
              "number_of_shards": 2
            }

        def save(self, **kwargs):
            # assign now if no timestamp given
            if not self.timestamp:
                self.timestamp = datetime.now()

            # override the index to go to the proper timeslot
            kwargs['index'] = self.timestamp.strftime('logs-%Y%m%d')
            return super().save(**kwargs)

    # once, as part of application setup, during deploy/migrations:
    logs = Log._index.as_template('logs', order=0)
    logs.save()

    # to perform search across all logs:
    search = Log.search()
