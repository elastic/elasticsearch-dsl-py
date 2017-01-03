from .connections import connections
from .search import Search

class Index(object):
    def __init__(self, name, using='default'):
        """
        :arg name: name of the index
        :arg using: connection alias to use, defaults to ``'default'``
        """
        self._name = name
        self._doc_types = {}
        self._mappings = {}
        self._using = using
        self._settings = {}
        self._aliases = {}
        self._analysis = {}

    def clone(self, name, using=None):
        """
        Create a copy of the instance with another name or connection alias.
        Useful for creating multiple indices with shared configuration::

            i = Index('base-index')
            i.settings(number_of_shards=1)
            i.create()

            i2 = i.clone('other-index')
            i2.create()

        :arg name: name of the index
        :arg using: connection alias to use, defaults to ``'default'``
        """
        i = Index(name, using=using or self._using)
        for attr in ('_doc_types', '_mappings', '_settings', '_aliases'):
            setattr(i, attr, getattr(self, attr).copy())
        return i


    def _get_connection(self):
        return connections.get_connection(self._using)
    connection = property(_get_connection)

    def doc_type(self, doc_type):
        """
        Associate a :class:`~elasticsearch_dsl.DocType` subclass with an index.
        This means that, when this index is created, it will contain the
        mappings fo the ``DocType``. If the ``DocType`` class doesn't have a
        default index yet, name of the ``Index`` instance will be used. Can be
        used as a decorator::

            i = Index('blog')

            @i.doc_type
            class Post(DocType):
                title = Text()

            # create the index, including Post mappings
            i.create()

            # .search() will now return a Search object that will return
            # properly deserialized Post instances
            s = i.search()
        """
        name = doc_type._doc_type.name
        self._doc_types[name] = doc_type
        self._mappings[name] = doc_type._doc_type.mapping

        if not doc_type._doc_type.index:
            doc_type._doc_type.index = self._name
        return doc_type # to use as decorator???

    def settings(self, **kwargs):
        """
        Add settings to the index::

            i = Index('i')
            i.settings(number_of_shards=1, number_of_replicas=0)

        Multiple calls to ``settings`` will merge the keys, later overriding
        the earlier.
        """
        self._settings.update(kwargs)
        return self

    def aliases(self, **kwargs):
        """
        Add aliases to the index definition::

            i = Index('blog-v2')
            i.aliases(blog={}, published={'filter': Q('term', published=True)})
        """
        self._aliases.update(kwargs)
        return self

    def analyzer(self, analyzer):
        """
        Explicitly add an analyzer to an index. Note that all custom analyzers
        defined in mappings will also be created. This is useful for search analyzers.

        Example::

            from elasticsearch_dsl import analyzer, tokenizer

            my_analyzer = analyzer('my_analyzer',
                tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
                filter=['lowercase']
            )

            i = Index('blog')
            i.analyzer(my_analyzer)

        """
        d = analyzer.get_analysis_definition()
        # empty custom analyzer, probably already defined out of our control
        if not d:
            return

        # merge the definition
        # TODO: conflict detection/resolution
        for key in d:
            self._analysis.setdefault(key, {}).update(d[key])

    def search(self):
        """
        Rteurn a :class:`~elasticsearch_dsl.Search` object searching over this
        index and its ``DocType``\s.
        """
        return Search(
            using=self._using,
            index=self._name,
            doc_type=[self._doc_types.get(k, k) for k in self._mappings]
        )

    def _get_mappings(self):
        analysis, mappings = {}, {}
        for mapping in self._mappings.values():
            mappings.update(mapping.to_dict())
            a = mapping._collect_analysis()
            # merge the definition
            # TODO: conflict detection/resolution
            for key in a:
                analysis.setdefault(key, {}).update(a[key])

        return mappings, analysis

    def to_dict(self):
        out = {}
        if self._settings:
            out['settings'] = self._settings
        if self._aliases:
            out['aliases'] = self._aliases
        mappings, analysis = self._get_mappings()
        if mappings:
            out['mappings'] = mappings
        if analysis or self._analysis:
            for key in self._analysis:
                analysis.setdefault(key, {}).update(self._analysis[key])
            out.setdefault('settings', {})['analysis'] = analysis
        return out

    def exists(self, **kwargs):
        """
        Returns ``True`` if the index already exists in elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.exists`` unchanged.
        """
        return self.connection.indices.exists(index=self._name, **kwargs)

    def refresh(self, **kwargs):
        """
        Preforms a refresh operation on the index.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.refresh`` unchanged.
        """
        return self.connection.indices.refresh(index=self._name, **kwargs)

    def flush(self, **kwargs):
        """
        Preforms a flush operation on the index.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.flush`` unchanged.
        """
        return self.connection.indices.flush(index=self._name, **kwargs)

    def open(self, **kwargs):
        """
        Opens the index in elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.open`` unchanged.
        """
        return self.connection.indices.open(index=self._name, **kwargs)

    def close(self, **kwargs):
        """
        Closes the index in elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.close`` unchanged.
        """
        return self.connection.indices.close(index=self._name, **kwargs)

    def create(self, **kwargs):
        """
        Creates the index in elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.create`` unchanged.
        """
        self.connection.indices.create(index=self._name, body=self.to_dict(), **kwargs)

    def delete(self, **kwargs):
        """
        Deletes the index in elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.delete`` unchanged.
        """
        self.connection.indices.delete(index=self._name, **kwargs)
