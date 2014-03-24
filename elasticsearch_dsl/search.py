import operator

from .query import Q, EMPTY_QUERY
from .filter import F, EMPTY_FILTER
from .aggs import AggBase
from .utils import DslBase

OPERATORS = {
    'add': operator.add,
    'and': operator.and_,

    # this should just add to .should?
    'or': operator.or_,
    'not': lambda a, b: operator.add(a, operator.invert(b)),
}

class BaseProxy(object):
    def __init__(self, search):
        self._search = search
        self._proxied = self._empty

    def __nonzero__(self):
        return self._proxied != self._empty
    __bool__ = __nonzero__

    def __call__(self, *args, **kwargs):
        op = kwargs.pop('operator', 'add')
        try:
            op = OPERATORS[op]
        except KeyError:
            raise #XXX
        self._proxied = op(self._proxied, self._shortcut(*args, **kwargs))

        # always return search to be chainable
        return self._search

    def __getattr__(self, attr_name):
        return getattr(self._proxied, attr_name)

    def __setattr__(self, attr_name, value):
        if not attr_name.startswith('_'):
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

        self.query = ProxyQuery(self)
        self.filter = ProxyFilter(self)
        self.post_filter = ProxyFilter(self)
        self.aggs = AggsProxy(self)

    def index(self, *index):
        # .index() resets
        if not index:
            self._index = None
        elif self._index is None:
            self._index = list(index)
        else:
            self._index.extend(index)

    def doc_type(self, *doc_type):
        # .doc_type() resets
        if not doc_type:
            self._doc_type = None
        elif self._doc_type is None:
            self._doc_type = list(doc_type)
        else:
            self._doc_type.extend(doc_type)

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
            print(self.post_filter._proxied, self.post_filter._empty)
            print(bool(self.post_filter))
            d['post_filter'] = self.post_filter.to_dict()

        if self.aggs.aggs:
            d.update(self.aggs.to_dict())

        d.update(kwargs)
        return d

