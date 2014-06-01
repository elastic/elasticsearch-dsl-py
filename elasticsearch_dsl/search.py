from .query import Q, EMPTY_QUERY, FilteredQuery
from .filter import F, EMPTY_FILTER
from .aggs import A, AggBase
from .utils import DslBase
from .result import Response


class BaseProxy(object):
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
    def __init__(self, using=None, index=None, doc_type=None):
        self._using = using

        self._index = None
        if isinstance(index, (tuple, list)):
            self._index = list(index)
        elif index:
            self._index = [index]

        self._doc_type = None
        if isinstance(doc_type, (tuple, list)):
            self._doc_type = list(doc_type)
        elif doc_type:
            self._doc_type = [doc_type]

        self.query = ProxyQuery(self, 'query')
        self.filter = ProxyFilter(self, 'filter')
        self.post_filter = ProxyFilter(self, 'post_filter')
        self.aggs = AggsProxy(self)
        self._sort = []

    @classmethod
    def from_dict(cls, d):
        s = cls()
        s.update_from_dict(d)
        return s

    def _clone(self):
        s = Search(using=self._using, index=self._index, doc_type=self._doc_type)
        s._sort = self._sort[:]
        for x in ('query', 'filter', 'post_filter'):
            getattr(s, x)._proxied = getattr(self, x)._proxied

        # copy top-level bucket definitions
        if self.aggs._params.get('aggs'):
            s.aggs._params = {'aggs': self.aggs._params['aggs'].copy()}
        return s

    def update_from_dict(self, d):
        self.query._proxied = Q(d['query'])
        if 'post_filter' in d:
            self.post_filter._proxied = F(d['post_filter'])

        if isinstance(self.query._proxied, FilteredQuery):
            self.filter._proxied = self.query._proxied.filter
            self.query._proxied = self.query._proxied.query

        aggs = d.get('aggs', d.get('aggregations', {}))
        if aggs:
            self.aggs._params = {
                'aggs': dict(
                    (name, A({name: value})) for (name, value) in aggs.items())
            }

    def sort(self, *keys):
        s = self._clone()
        s._sort = []
        for k in keys:
            if isinstance(k, str) and k.startswith('-'):
                k = {k[1:]: {"order": "desc"}}
            s._sort.append(k)
        return s

    def index(self, *index):
        # .index() resets
        s = self._clone()
        if not index:
            s._index = None
        else:
            s._index = (self._index or []) + list(index)
        return s

    def doc_type(self, *doc_type):
        # .doc_type() resets
        s = self._clone()
        if not doc_type:
            s._doc_type = None
        else:
            s._doc_type = (self._doc_type or []) + list(doc_type)
        return s

    def to_dict(self, **kwargs):
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

        if self.aggs.aggs:
            d.update(self.aggs.to_dict())

        if self._sort:
            d['sort'] = self._sort

        d.update(kwargs)
        return d

    def using(self, client):
        s = self._clone()
        s._using = client
        return s

    def count(self):
        if not self._using:
            raise #XXX

        d = self.to_dict()
        # TODO: failed shards detection
        # TODO: remove aggs etc?
        return self._using.count(
            index=self._index,
            doc_type=self._doc_type,
            body=d
        )['count']

    def execute(self, **kwargs):
        if not self._using:
            raise #XXX

        return Response(
            self._using.search(
                index=self._index,
                doc_type=self._doc_type,
                body=self.to_dict(),
                **kwargs
            )
        )

