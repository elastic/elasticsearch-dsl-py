from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin
from .function import SF, ScoreFunction

class QueryMeta(DslMeta):
    _classes = {}

def Q(name_or_query, **params):
    # {"match": {"title": "python"}}
    if isinstance(name_or_query, dict):
        if params:
            raise ValueError('Q() cannot accept parameters when passing in a dict.')
        if len(name_or_query) != 1:
            raise ValueError('Q() can only accept dict with a single query ({"match": {...}}). '
                 'Instead it got (%r)' % name_or_query)
        name, params = name_or_query.copy().popitem()
        return Query.get_dsl_class(name)(**params)

    # MatchAll()
    if isinstance(name_or_query, Query):
        if params:
            raise ValueError('Q() cannot accept parameters when passing in a Query object.')
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

class MultiMatch(Query):
    name = 'multi_match'

class QueryString(Query):
    name = 'query_string'

class Fuzzy(Query):
    name = 'fuzzy'

class Prefix(Query):
    name = 'prefix'

class Term(Query):
    name = 'term'

class HasChild(Query):
    name = 'has_child'
    _param_defs = {'query': {'type': 'query'}}

class HasParent(Query):
    name = 'has_parent'
    _param_defs = {'query': {'type': 'query'}}

class Bool(BoolMixin, Query):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'query', 'multi': True},
        'should': {'type': 'query', 'multi': True},
        'must_not': {'type': 'query', 'multi': True},
    }

# register this as Bool for Query
Query._bool = Bool

class Filtered(Query):
    name = 'filtered'
    _param_defs = {
        'query': {'type': 'query'},
        'filter': {'type': 'filter'},
    }

class FunctionScore(Query):
    name = 'function_score'
    _param_defs = {
        'query': {'type': 'query'},
        'filter': {'type': 'filter'},
        'functions': {'type': 'score_function', 'multi': True},
    }

    def __init__(self, **kwargs):
        if 'functions' in kwargs:
            pass
        else:
            fns = kwargs['functions'] = []
            for name in ScoreFunction._classes:
                if name in kwargs:
                    fns.append({name: kwargs.pop(name)})
        super(FunctionScore, self).__init__(**kwargs)
