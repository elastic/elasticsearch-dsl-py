.. _persistence:

Persistence
===========

You can use the dsl library to define your mappings and a basic persistent
layer for your application.

Mappings
--------

The mapping definition follows a similar pattern to the query dsl:

.. code:: python

    from elasticsearch_dsl import Mapping, String, Nested

    # name your type
    m = Mapping('my-type')

    # add fields
    m.field('title', 'string')

    # you can use multi-fields easily
    m.field('category', 'string', fields={'raw': String(index='not_analyzed')})

    # you can also create a field manually
    comment = Nested()
    comment.field('author', String())
    comment.field('created_at', Date())

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
    (``m.field('tags', String(index='not_analyzed', multi=True))``). Then the
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

DocType
-------

If you want to create a model-like wrapper around your documents, use the
``DocType`` class:

.. code:: python

    from datetime import datetime
    from elasticsearch_dsl import DocType, String, Date, Nested, Boolean

    class Post(DocType):
        title = String()
        created_at = Date()
        published = Boolean()
        category = String(fields={'raw': String(index='not_analyzed')})

        comments = Nested(
            properties={
              'author': String(fields={'raw': String(index='not_analyzed')}),
              'content': String(analyzer='snowball'),
              'created_at': Date()
            }
        )

        class Meta:
            index = 'blog'

        def add_comment(self, author, content):
            self.comments.append(
              {'author': author, 'content': content})

        def save(self, ** kwargs):
            self.created_at = datetime.now()
            return super().save(** kwargs)


Document life cycle
~~~~~~~~~~~~~~~~~~~

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


All the metadata fields (``id``, ``parent``, ``routing``, ``index`` etc) can be
accessed (and set) via a ``meta`` attribute or directly using the underscored
variant:

.. code:: python

    post = Post(meta={'id': 42})

    # prints 42, same as post._id
    print(post.meta.id)

    # override default index
    post._index = 'my-blog'

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
    for posts in results:
        print(post.meta.score, post.title)

Alternatively you can just take a ``Search`` object and restrict it to return
our document type, wrapped in correct class:

.. code:: python

    s = Search()
    s = s.doc_type(Post)

You can also combine document classes with standard doc types (just strings),
which will be treated as before. You can also pass in multiple ``DocType``
subclasses and each document in the response will be wrapped in it's class.

To delete a document just call its ``delete`` method:

.. code:: python

    first = Post.get(id=42)
    first.delete()

``class Meta`` options
~~~~~~~~~~~~~~~~~~~~~~

In the ``Meta`` class inside your document definition you can define various
metadata for your document:

``doc_type``
  name of the doc_type in elasticsearch. By default it will be constructed from
  the class name (MyDocument -> my_document)

``index``
  default index for the document, by default it is empty and every operation
  such as ``get`` or ``save`` requires an explicit ``index`` parameter

``using``
  default connection alias to use, defaults to ``'default'``

``mapping``
  optional instance of ``Mapping`` class to use as base for the mappings
  created from the fields on the document class itself.

Any attributes on the ``Meta`` class that are instance of ``MetaField`` will be
used to control the mapping of the mata fields (``_all``, ``_parent`` etc).
Just name the parameter (without the leading underscore) as the field you wish
to map and pass any parameters to the ``MetaField`` class:

.. code:: python

    class Post(DocType):
        title = String()

        class Meta:
            all = MetaField(enabled=False)
            parent = MetaField(type='blog')

