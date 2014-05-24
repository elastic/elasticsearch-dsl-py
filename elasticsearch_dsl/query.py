from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin

class QueryMeta(DslMeta):
    _classes = {}

def Q(name_or_query, **params):
    # {"match": {"title": "python"}}
    if isinstance(name_or_query, dict):
        if params:
            raise #XXX
        if len(name_or_query) != 1:
            raise #XXX
        name, params = name_or_query.copy().popitem()
        return Query.get_dsl_class(name)(**params)

    # MatchAll()
    if isinstance(name_or_query, Query):
        if params:
            raise #XXX
        return name_or_query

    # "match", title="python"
    return Query.get_dsl_class(name_or_query)(**params)

@add_metaclass(QueryMeta)
class Query(DslBase):
    _type_name = 'query'
    _type_shortcut = staticmethod(Q)
    name = None

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

# register this as Bool for Query
Query._bool = Bool

class FilteredQuery(Query):
    name = 'filtered'
    _param_defs = {
        'query': {'type': 'query'},
        'filter': {'type': 'filter'},
    }
