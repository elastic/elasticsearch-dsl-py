from six import iteritems, string_types

from elasticsearch.helpers import scan

from .query import Q, EMPTY_QUERY, Filtered
from .filter import F, EMPTY_FILTER
from .aggs import A, AggBase
from .utils import DslBase
from .result import Response, Result
from .connections import connections

class BaseProxy(object):
    """
    Simple proxy around DSL objects (queries and filters) that can be called
    (to add query/filter) and also allows attribute access which is proxied to
    the wrapped query/filter.
    """
    def __init__(self, search, attr_name):
        self._search = search
        self._proxied = self._empty
        self._attr_name = attr_name

    def __nonzero__(self):
        return self._proxied != self._empty
    __bool__ = __nonzero__

    def __call__(self, *args, **kwargs):
        s = self._search._clone()
        getattr(s, self._attr_name)._proxied += self._shortcut(*args, **kwargs)

        # always return search to be chainable
        return s

    def __getattr__(self, attr_name):
        return getattr(self._proxied, attr_name)

    def __setattr__(self, attr_name, value):
        if not attr_name.startswith('_'):
            self._proxied = self._shortcut(self._proxied.to_dict())
            setattr(self._proxied, attr_name, value)
        super(BaseProxy, self).__setattr__(attr_name, value)


class ProxyDescriptor(object):
    """
    Simple descriptor to enable setting of queries and filters as:

        s = Search()
        s.query = Q(...)

    """
    def __init__(self, name):
        self._attr_name = '_%s_proxy' % name

    def __get__(self, instance, owner):
        return getattr(instance, self._attr_name)

    def __set__(self, instance, value):
        proxy = getattr(instance, self._attr_name)
        proxy._proxied = proxy._shortcut(value)


class ProxyQuery(BaseProxy):
    _empty = EMPTY_QUERY
    _shortcut = staticmethod(Q)


class ProxyFilter(BaseProxy):
    _empty = EMPTY_FILTER
    _shortcut = staticmethod(F)


class AggsProxy(AggBase, DslBase):
    name = 'aggs'
    def __init__(self, search):
        self._base = self._search = search
        self._params = {'aggs': {}}

    def to_dict(self):
        return super(AggsProxy, self).to_dict().get('aggs', {})


class Search(object):
    query = ProxyDescriptor('query')
    filter = ProxyDescriptor('filter')
    post_filter = ProxyDescriptor('post_filter')

    def __init__(self, using='default', index=None, doc_type=None, extra=None):
        """
        Search request to elasticsearch.

        :arg using: `Elasticsearch` instance to use
        :arg index: limit the search to index
        :arg doc_type: only query this type.

        All the paramters supplied (or omitted) at creation type can be later
        overriden by methods (`using`, `index` and `doc_type` respectively).
        """
        self._using = using

        self._index = None
        if isinstance(index, (tuple, list)):
            self._index = list(index)
        elif index:
            self._index = [index]

        self._doc_type = []
        self._doc_type_map = {}
        if isinstance(doc_type, (tuple, list)):
            for dt in doc_type:
                self._add_doc_type(dt)
        elif isinstance(doc_type, dict):
            self._doc_type.extend(doc_type.keys())
            self._doc_type_map.update(doc_type)
        elif doc_type:
            self._add_doc_type(doc_type)

        self.aggs = AggsProxy(self)
        self._sort = []
        self._extra = extra or {}
        self._params = {}
        self._fields = None
        self._partial_fields = {}
        self._highlight = {}
        self._highlight_opts = {}
        self._suggest = {}
        self._script_fields = {}

        self._query_proxy = ProxyQuery(self, 'query')
        self._filter_proxy = ProxyFilter(self, 'filter')
        self._post_filter_proxy = ProxyFilter(self, 'post_filter')

    def __getitem__(self, n):
        """
        Support slicing the `Search` instance for pagination.

        Slicing equates to the from/size parameters. E.g.::

            s = Search().query(...)[0:25]

        is equivalent to::

            s = Search().query(...).extra(from_=0, size=25)

        """
        s = self._clone()

        if isinstance(n, slice):
            # If negative slicing, abort.
            if n.start and n.start < 0 or n.stop and n.stop < 0:
                raise ValueError("Search does not support negative slicing.")
            # Elasticsearch won't get all results so we default to size: 10 if
            # stop not given.
            s._extra['from'] = n.start or 0
            s._extra['size'] = n.stop - (n.start or 0) if n.stop is not None else 10
            return s
        else:  # This is an index lookup, equivalent to slicing by [n:n+1].
            # If negative index, abort.
            if n < 0:
                raise ValueError("Search does not support negative indexing.")
            s._extra['from'] = n
            s._extra['size'] = 1
            return s

    @classmethod
    def from_dict(cls, d):
        """
        Construct a `Search` instance from a raw dict containing the search
        body. Useful when migrating from raw dictionaries.

        Example::

            s = Search.from_dict({
                "query": {
                    "bool": {
                        "must": [...]
                    }
                },
                "aggs": {...}
            })
            s = s.filter('term', published=True)
        """
        s = cls()
        s.update_from_dict(d)
        return s

    def _clone(self):
        """
        Return a clone of the current search request. Performs a shallow copy
        of all the underlying objects. Used internally by most state modifying
        APIs.
        """
        s = self.__class__(using=self._using, index=self._index,
                           doc_type=self._doc_type)
        s._doc_type_map = self._doc_type_map.copy()
        s._sort = self._sort[:]
        s._fields = self._fields[:] if self._fields is not None else None
        s._partial_fields = self._partial_fields.copy()
        s._extra = self._extra.copy()
        s._highlight = self._highlight.copy()
        s._highlight_opts = self._highlight_opts.copy()
        s._suggest = self._suggest.copy()
        s._script_fields = self._script_fields.copy()
        for x in ('query', 'filter', 'post_filter'):
            getattr(s, x)._proxied = getattr(self, x)._proxied

        # copy top-level bucket definitions
        if self.aggs._params.get('aggs'):
            s.aggs._params = {'aggs': self.aggs._params['aggs'].copy()}
        s._params = self._params.copy()
        return s

    def update_from_dict(self, d):
        """
        Apply options from a serialized body to the current instance. Modifies
        the object in-place. Used mostly by ``from_dict``.
        """
        d = d.copy()
        if 'query' in d:
            self.query._proxied = Q(d.pop('query'))
        if 'post_filter' in d:
            self.post_filter._proxied = F(d.pop('post_filter'))

        if isinstance(self.query._proxied, Filtered):
            self.filter._proxied = self.query._proxied.filter
            self.query._proxied = self.query._proxied.query

        aggs = d.pop('aggs', d.pop('aggregations', {}))
        if aggs:
            self.aggs._params = {
                'aggs': dict(
                    (name, A(value)) for (name, value) in iteritems(aggs))
            }
        if 'sort' in d:
            self._sort = d.pop('sort')
        if 'fields' in d:
            self._fields = d.pop('fields')
        if 'partial_fields' in d:
            self._partial_fields = d.pop('partial_fields')
        if 'highlight' in d:
            high = d.pop('highlight').copy()
            self._highlight = high.pop('fields')
            self._highlight_opts = high
        if 'suggest' in d:
            self._suggest = d.pop('suggest')
            if 'text' in self._suggest:
                text = self._suggest.pop('text')
                for s in self._suggest.values():
                    s.setdefault('text', text)
        if 'script_fields' in d:
            self._script_fields = d.pop('script_fields')
        self._extra = d

    def script_fields(self, **kwargs):
        """
        Define script fields to be calculated on hits. See
        https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-script-fields.html
        for more details.

        Example::

            s = Search()
            s = s.script_fields(times_two="doc['field'].value * 2")
            s = s.script_fields(
                times_three={
                    'script': "doc['field'].value * n",
                    'params': {'n': 3}
                }
            )
        
        """
        s = self._clone()
        for name in kwargs:
            if isinstance(kwargs[name], string_types):
                kwargs[name] = {'script': kwargs[name]}
        s._script_fields.update(kwargs)
        return s

    def params(self, **kwargs):
        """
        Specify query params to be used when executing the search. All the
        keyword arguments will override the current values. See
        http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch.search
        for all availible parameters.

        Example::

            s = Search()
            s = s.params(routing='user-1', preference='local')
        """
        s = self._clone()
        s._params.update(kwargs)
        return s

    def extra(self, **kwargs):
        """
        Add extra keys to the request body. Mostly here for backwards
        compatibility.
        """
        s = self._clone()
        if 'from_' in kwargs:
            kwargs['from'] = kwargs.pop('from_')
        s._extra.update(kwargs)
        return s

    def fields(self, fields=None):
        """
        Selectively load specific stored fields for each document.

        :arg fields: list of fields to return for each document

        If ``fields`` is None, the entire document will be returned for
        each hit.  If fields is the empty list, no fields will be
        returned for each hit, just the metadata.
        """
        s = self._clone()
        s._fields = fields
        return s

    def partial_fields(self, **partial):
        """
        Control which part of the fields to extract from the `_source` document

        :kwargs partial: dict specifying which fields to extract from the source

        An example usage would be:

            s = Search().partial_fields(authors_data={
                    'include': ['authors.*'],
                    'exclude': ['authors.name']
                })

        which will include all fields from the `authors` nested property except for
        each authors `name`

        If ``partial`` is not provided, the whole `_source` will be fetched. Calling this multiple
        times will override the previous values with the new ones.
        """
        s = self._clone()
        s._partial_fields = partial
        return s

    def sort(self, *keys):
        """
        Add sorting information to the search request. If called without
        arguments it will remove all sort requirements. Otherwise it will
        replace them. Acceptable arguments are::

            'some.field'
            '-some.other.field'
            {'different.field': {'any': 'dict'}}

        so for example::

            s = Search().sort(
                'category',
                '-title',
                {"price" : {"order" : "asc", "mode" : "avg"}}
            )

        will sort by ``category``, ``title`` (in descending order) and
        ``price`` in ascending order using the ``avg`` mode.

        The API returns a copy of the Search object and can thus be chained.
        """
        s = self._clone()
        s._sort = []
        for k in keys:
            if isinstance(k, string_types) and k.startswith('-'):
                k = {k[1:]: {"order": "desc"}}
            s._sort.append(k)
        return s

    def highlight_options(self, **kwargs):
        """
        Update the global highlighting options used for this request. For
        example::

            s = Search()
            s = s.highlight_options(order='score')
        """
        s = self._clone()
        s._highlight_opts.update(kwargs)
        return s

    def highlight(self, *fields, **kwargs):
        """
        Request highliting of some fields. All keyword arguments passed in will be
        used as parameters. Example::

            Search().highlight('title', 'body', fragment_size=50)

        will produce the equivalent of::

            {
                "highlight": {
                    "fields": {
                        "body": {"fragment_size": 50},
                        "title": {"fragment_size": 50}
                    }
                }
            }

        """
        s = self._clone()
        for f in fields:
            s._highlight[f] = kwargs
        return s

    def suggest(self, name, text, **kwargs):
        """
        Add a suggestions request to the search.

        :arg name: name of the suggestion
        :arg text: text to suggest on

        All keyword arguments will be added to the suggestions body. For example::

            s = Search()
            s = s.suggest('suggestion-1', 'Elasticserach', term={'field': 'body'})
        """
        s = self._clone()
        s._suggest[name] = {'text': text}
        s._suggest[name].update(kwargs)
        return s

    def index(self, *index):
        """
        Set the index for the search. If called empty it will rmove all information.

        Example:

            s = Search()
            s = s.index('twitter-2015.01.01', 'twitter-2015.01.02')
        """
        # .index() resets
        s = self._clone()
        if not index:
            s._index = None
        else:
            s._index = (self._index or []) + list(index)
        return s

    def _add_doc_type(self, doc_type):
        if hasattr(doc_type, '_doc_type'):
            self._doc_type_map[doc_type._doc_type.name] = doc_type.from_es
            doc_type = doc_type._doc_type.name
        self._doc_type.append(doc_type)

    def doc_type(self, *doc_type, **kwargs):
        """
        Set the type to search through. You can supply a single value or
        multiple. Values can be strings or subclasses of ``DocType``.
        
        You can also pass in any keyword arguments, mapping a doc_type to a
        callback that should be used instead of the Result class.

        If no doc_type is supplied any information stored on the instance will
        be erased.

        Example:

            s = Search().doc_type('product', 'store', User, custom=my_callback)
        """
        # .doc_type() resets
        s = self._clone()
        if not doc_type and not kwargs:
            s._doc_type = []
            s._doc_type_map = {}
        else:
            for dt in doc_type:
                s._add_doc_type(dt)
            s._doc_type.extend(kwargs.keys())
            s._doc_type_map.update(kwargs)
        return s

    def to_dict(self, count=False, **kwargs):
        """
        Serialize the search into the dictionary that will be sent over as the
        request's body.

        :arg count: a flag to specify we are interested in a body for count -
            no aggregations, no pagination bounds etc.

        All additional keyword arguments will be included into the dictionary.
        """
        if self.filter:
            d = {
              "query": {
                "filtered": {
                  "query": self.query.to_dict(),
                  "filter": self.filter.to_dict()
                }
              }
            }
        else:
            d = {"query": self.query.to_dict()}

        if self.post_filter:
            d['post_filter'] = self.post_filter.to_dict()

        # count request doesn't care for sorting and other things
        if not count:
            if self.aggs.aggs:
                d.update(self.aggs.to_dict())

            if self._sort:
                d['sort'] = self._sort

            d.update(self._extra)

            if self._fields is not None:
                d['fields'] = self._fields

            if self._partial_fields:
                d['partial_fields'] = self._partial_fields

            if self._highlight:
                d['highlight'] = {'fields': self._highlight}
                d['highlight'].update(self._highlight_opts)

            if self._suggest:
                d['suggest'] = self._suggest

            if self._script_fields:
                d['script_fields'] = self._script_fields

        d.update(kwargs)
        return d

    def using(self, client):
        """
        Associate the search request with an elasticsearch client. A fresh copy
        will be returned with current instance remaining unchanged.

        :arg client: an instance of ``elasticsearch.Elasticsearch`` to use or
            an alias to look up in ``elasticsearch_dsl.connections``

        """
        s = self._clone()
        s._using = client
        return s

    def count(self):
        """
        Return the number of hits matching the query and filters. Note that
        only the actual number is returned.
        """
        es = connections.get_connection(self._using)

        d = self.to_dict(count=True)
        # TODO: failed shards detection
        return es.count(
            index=self._index,
            doc_type=self._doc_type,
            body=d
        )['count']

    def execute(self, response_class=Response):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg response_class: optional subclass of ``Response`` to use instead.
        """
        es = connections.get_connection(self._using)

        return response_class(
            es.search(
                index=self._index,
                doc_type=self._doc_type,
                body=self.to_dict(),
                **self._params
            ),
            callbacks=self._doc_type_map
        )

    def scan(self):
        """
        Turn the search into a scan search and return a generator that will
        iterate over all the documents matching the query.

        Use ``params`` method to specify any additional arguments you with to
        pass to the underlying ``scan`` helper from ``elasticsearch-py`` -
        http://elasticsearch-py.readthedocs.org/en/master/helpers.html#elasticsearch.helpers.scan

        """
        es = connections.get_connection(self._using)

        for hit in scan(
                es,
                query=self.to_dict(),
                index=self._index,
                doc_type=self._doc_type,
                **self._params
            ):
            yield self._doc_type_map.get(hit['_type'], Result)(hit)

