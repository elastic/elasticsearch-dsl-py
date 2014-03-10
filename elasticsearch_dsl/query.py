from six import add_metaclass

from .utils import DslMeta, DslBase

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
    _type_shortcut = Q
    name = None

    def __add__(self, other):
        return Bool(must=[self, other])

class MatchAll(Query):
    name = 'match_all'
    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other

EMPTY_QUERY = MatchAll()

class Match(Query):
    name = 'match'

class Bool(Query):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'query', 'multi': True},
        'should': {'type': 'query', 'multi': True},
        'must_not': {'type': 'query', 'multi': True},
    }

