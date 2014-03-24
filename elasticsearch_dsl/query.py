from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin

class QueryMeta(DslMeta):
    _classes = {}

def Q(name_or_query, **params):
    if isinstance(name_or_query, dict):
        if params:
            raise #XXX
        if len(name_or_query) != 1:
            raise #XXX
        name, params = name_or_query.popitem()
        return Query.get_dsl_class(name)(**params)
    if isinstance(name_or_query, Query):
        if params:
            raise #XXX
        return name_or_query
    return Query.get_dsl_class(name_or_query)(**params)

@add_metaclass(QueryMeta)
class Query(DslBase):
    _type_name = 'query'
    _type_shortcut = staticmethod(Q)
    name = None

    def __add__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__radd__'):
            return other.__radd__(self)
        return Bool(must=[self, other])

    def __invert__(self):
        return Bool(must_not=[self])

    def __or__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__ror__'):
            return other.__ror__(self)
        return Bool(should=[self, other])

    def __and__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__rand__'):
            return other.__rand__(self)
        return Bool(must=[self, other])

class MatchAll(Query):
    name = 'match_all'
    def __add__(self, other):
        return other._clone()
    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other):
        return self
    __ror__ = __or__

EMPTY_QUERY = MatchAll()

class Match(Query):
    name = 'match'

class Bool(BoolMixin, Query):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'query', 'multi': True},
        'should': {'type': 'query', 'multi': True},
        'must_not': {'type': 'query', 'multi': True},
    }

