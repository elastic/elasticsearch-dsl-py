import operator

from .query import Q, EMPTY_QUERY
from .aggs import AggBase
from .utils import DslBase

OPERATORS = {
    'add': operator.add,
    'and': operator.and_,

    # this should just add to .should?
    'or': operator.or_,
    'not': lambda a, b: operator.add(a, operator.invert(b)),
}

class ProxyQuery(object):
    def __init__(self, search):
        self._search = search
        self._query = EMPTY_QUERY

    def __call__(self, *args, **kwargs):
        op = kwargs.pop('operator', 'add')
        try:
            op = OPERATORS[op]
        except KeyError:
            raise #XXX
        self._query = op(self._query, Q(*args, **kwargs))

        # always return search to be chainable
        return self._search

    def __getattr__(self, attr_name):
        return getattr(self._query, attr_name)

    def __setattr__(self, attr_name, value):
        if not attr_name.startswith('_'):
            setattr(self._query, attr_name, value)
        super(ProxyQuery, self).__setattr__(attr_name, value)

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
        d = {"query": self.query.to_dict()}
        if self.aggs.aggs:
            d.update(self.aggs.to_dict())
        d.update(kwargs)
        return d

