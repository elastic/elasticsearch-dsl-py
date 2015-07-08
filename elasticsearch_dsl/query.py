from .utils import DslBase, BoolMixin, _make_dsl_class
from .function import SF, ScoreFunction

__all__ = ['Bool', 'BoolMixin', 'Boosting', 'Common', 'ConstantScore', 'DisMax',
           'DslBase', 'Filtered', 'FunctionScore', 'Fuzzy', 'FuzzyLikeThis',
           'FuzzyLikeThisField', 'GeoShape', 'HasChild', 'HasParent', 'Ids',
           'Indices', 'Match', 'MatchAll', 'MatchPhrase', 'MatchPhrasePrefix',
           'MoreLikeThis', 'MoreLikeThisField', 'MultiMatch', 'Nested',
           'Prefix', 'Q', 'Query', 'QueryString', 'Range', 'Regexp', 'SF',
           'ScoreFunction', 'SimpleQueryString', 'SpanFirst', 'SpanMulti',
           'SpanNear', 'SpanNot', 'SpanOr', 'SpanTerm', 'Template', 'Term',
           'Terms', 'TopChildren', 'Wildcard']


def Q(name_or_query='match_all', **params):
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

    # s.query = Q('filtered', query=s.query)
    if hasattr(name_or_query, '_proxied'):
        return name_or_query._proxied

    # "match", title="python"
    return Query.get_dsl_class(name_or_query)(**params)

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

class Bool(BoolMixin, Query):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'query', 'multi': True},
        'should': {'type': 'query', 'multi': True},
        'must_not': {'type': 'query', 'multi': True},
    }
# register this as Bool for Query
Query._bool = Bool

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

QUERIES = (
    # compound queries
    ('boosting', {'positive': {'type': 'query'}, 'negative': {'type': 'query'}}),
    ('constant_score', {'query': {'type': 'query'}, 'filter': {'type': 'filter'}}),
    ('dis_max', {'queries': {'type': 'query', 'multi': True}}),
    ('filtered', {'query': {'type': 'query'}, 'filter': {'type': 'filter'}}),
    ('indices', {'query': {'type': 'query'}, 'no_match_query': {'type': 'query'}}),

    # relationship queries
    ('nested', {'query': {'type': 'query'}}),
    ('has_child', {'query': {'type': 'query'}}),
    ('has_parent', {'query': {'type': 'query'}}),
    ('top_children', {'query': {'type': 'query'}}),

    # compount span queries
    ('span_first', {'match': {'type': 'query'}}),
    ('span_multi', {'match': {'type': 'query'}}),
    ('span_near', {'clauses': {'type': 'query', 'multi': True}}),
    ('span_not', {'exclude': {'type': 'query'}, 'include': {'type': 'query'}}),
    ('span_or', {'clauses': {'type': 'query', 'multi': True}}),

    # core queries
    ('common', None),
    ('fuzzy', None),
    ('fuzzy_like_this', None),
    ('fuzzy_like_this_field', None),
    ('geo_shape', None),
    ('ids', None),
    ('match', None),
    ('match_phrase', None),
    ('match_phrase_prefix', None),
    ('more_like_this', None),
    ('more_like_this_field', None),
    ('multi_match', None),
    ('prefix', None),
    ('query_string', None),
    ('range', None),
    ('regexp', None),
    ('simple_query_string', None),
    ('span_term', None),
    ('template', None),
    ('term', None),
    ('terms', None),
    ('wildcard', None),
)

# generate the query classes dynamicaly
for qname, params_def in QUERIES:
    qclass = _make_dsl_class(Query, qname, params_def)
    globals()[qclass.__name__] = qclass

