import copy
from six import iteritems

from .search import Request, QueryProxy, ProxyDescriptor
from .query import Q, Bool
from .response import UpdateByQueryResponse
from .connections import connections

class UpdateByQuery(Request):

    query = ProxyDescriptor('query')

    def __init__(self, **kwargs):
        """
        Update by query request to elasticsearch.

        :arg using: `Elasticsearch` instance to use
        :arg index: limit the search to index
        :arg doc_type: only query this type.

        All the parameters supplied (or omitted) at creation type can be later
        overriden by methods (`using`, `index` and `doc_type` respectively).

        """
        super(UpdateByQuery, self).__init__(**kwargs)
        self._response_class = UpdateByQueryResponse
        self._source = None
        self._script = {}
        self._query_proxy = QueryProxy(self, 'query')

    def filter(self, *args, **kwargs):
        return self.query(Bool(filter=[Q(*args, **kwargs)]))

    def exclude(self, *args, **kwargs):
        return self.query(Bool(filter=[~Q(*args, **kwargs)]))

    @classmethod
    def from_dict(cls, d):
        """
        Construct a new `UpdateByQuery` instance from a raw dict containing the search
        body. Useful when migrating from raw dictionaries.

        Example::

            ubq = UpdateByQuery.from_dict({
                "query": {
                    "bool": {
                        "must": [...]
                    }
                },
                "script": {...}
            })
            ubq = ubq.filter('term', published=True)
        """
        u = cls()
        u.update_from_dict(d)
        return u

    def _clone(self):
        """
        Return a clone of the current search request. Performs a shallow copy
        of all the underlying objects. Used internally by most state modifying
        APIs.
        """
        ubq = super(UpdateByQuery, self)._clone()

        ubq._response_class = self._response_class
        ubq._source = copy.copy(self._source) \
            if self._source is not None else None
        ubq._script = self._script.copy()
        getattr(ubq, 'query')._proxied = getattr(self, 'query')._proxied
        return ubq

    def response_class(self, cls):
        """
        Override the default wrapper used for the response.
        """
        ubq = self._clone()
        ubq._response_class = cls
        return ubq

    def update_from_dict(self, d):
        """
        Apply options from a serialized body to the current instance. Modifies
        the object in-place. Used mostly by ``from_dict``.
        """
        d = d.copy()
        if 'query' in d:
            self.query._proxied = Q(d.pop('query'))

        aggs = d.pop('aggs', d.pop('aggregations', {}))
        if aggs:
            self.aggs._params = {
                'aggs': dict(
                    (name, A(value)) for (name, value) in iteritems(aggs))
            }
        if '_source' in d:
            self._source = d.pop('_source')
        if 'script' in d:
            self._script = d.pop('script')
        self._extra = d
        return self

    def script(self, **kwargs):
        """
        Define update action to take:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-scripting-using.html
        for more details.

        Note: the API only accepts a single script, so calling the script multiple times will overwrite.

        Example::

            ubq = Search()
            ubq = ubq.script(source="ctx.__source.likes++"")
            ubq = ubq.script(source="ctx.__source.likes += params.f"",
                         lang="expression",
                         params={'f': 3})
        """
        ubq = self._clone()
        if ubq._script:
            ubq._script = {}
        ubq._script.update(kwargs)
        return ubq

    def source(self, fields=None, **kwargs):
        """
        Selectively control how the _source field is returned.

        :arg source: wildcard string, array of wildcards, or dictionary of includes and excludes

        If ``source`` is None, the entire document will be returned for
        each hit.  If source is a dictionary with keys of 'include' and/or
        'exclude' the fields will be either included or excluded appropriately.

        Calling this multiple times with the same named parameter will override the
        previous values with the new ones.

        Example::

            ubq = Search()
            ubq = ubq.source(include=['obj1.*'], exclude=["*.description"])

            ubq = Search()
            ubq = ubq.source(include=['obj1.*']).source(exclude=["*.description"])

        """
        ubq = self._clone()

        if fields and kwargs:
            raise ValueError("You cannot specify fields and kwargs at the same time.")

        if fields is not None:
            ubq._source = fields
            return ubq

        if kwargs and not isinstance(ubq._source, dict):
            ubq._source = {}

        for key, value in kwargs.items():
            if value is None:
                try:
                    del ubq._source[key]
                except KeyError:
                    pass
            else:
                ubq._source[key] = value

        return ubq

    def to_dict(self, **kwargs):
        """
        Serialize the search into the dictionary that will be sent over as the
        request'ubq body.

        All additional keyword arguments will be included into the dictionary.
        """
        d = {}
        if self.query:
            d["query"] = self.query.to_dict()

        if self._source not in (None, {}):
            d['_source'] = self._source

        if self._script:
            d['script'] = self._script

        d.update(self._extra)

        d.update(kwargs)
        return d

    def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg response_class: optional subclass of ``Response`` to use instead.
        """
        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)

            self._response = self._response_class(
                self,
                es.update_by_query(
                    index=self._index,
                    doc_type=self._get_doc_type(),
                    body=self.to_dict(),
                    **self._params
                )
            )
        return self._response
