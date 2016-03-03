from six import iteritems

from .utils import DslBase, _make_dsl_class
from .function import SF, ScoreFunction

__all__ = [
    'Q', 'Bool', 'Boosting', 'Common', 'ConstantScore', 'DisMax', 'Filtered',
    'FunctionScore', 'Fuzzy', 'FuzzyLikeThis', 'FuzzyLikeThisField',
    'GeoShape', 'HasChild', 'HasParent', 'Ids', 'Indices', 'Match', 'MatchAll',
    'MatchPhrase', 'MatchPhrasePrefix', 'MoreLikeThis', 'MoreLikeThisField',
    'MultiMatch', 'Nested', 'Prefix', 'Query', 'QueryString', 'Range',
    'Regexp', 'SF', 'ScoreFunction', 'SimpleQueryString', 'SpanFirst',
    'SpanMulti', 'SpanNear', 'SpanNot', 'SpanOr', 'SpanTerm', 'Template',
    'Term', 'Terms', 'TopChildren', 'Wildcard'
]


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
    def __add__(self, other):
        return other._clone()
    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other):
        return self
    __ror__ = __or__

    def __init__(self, **params):
        self._params = {}
        for pname, pvalue in iteritems(params):
            if '__' in pname:
                pname = pname.replace('__', '.')
            self._setattr(pname, pvalue)

    def to_dict(self):
        """
        Serialize the DSL object to plain dict
        """
        if 'field' not in self._params:
            return super(Match, self).to_dict()

        field_name = self._params.pop('field')
        d = {}
        for pname, value in iteritems(self._params):
            pinfo = self._param_defs.get(pname)

            # typed param
            if pinfo and 'type' in pinfo:
                # don't serialize empty lists and dicts for typed fields
                if value in ({}, []):
                    continue

                # multi-values are serialized as list of dicts
                if pinfo.get('multi'):
                    value = list(map(lambda x: x.to_dict(), value))

                # squash all the hash values into one dict
                elif pinfo.get('hash'):
                    value = dict((k, v.to_dict()) for k, v in iteritems(value))

                # serialize single values
                else:
                    value = value.to_dict()

            # serialize anything with to_dict method
            elif hasattr(value, 'to_dict'):
                value = value.to_dict()

            d[pname] = value
        return {self.name: {field_name: d}}


class Bool(Query):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'query', 'multi': True},
        'should': {'type': 'query', 'multi': True},
        'must_not': {'type': 'query', 'multi': True},
        'filter': {'type': 'query', 'multi': True},
    }

    def __add__(self, other):
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
            q.filter += other.filter
        else:
            q.must.append(other)
        return q
    __radd__ = __add__

    def __or__(self, other):
        for q in (self, other):
            if isinstance(q, Bool) and len(q.should) == 1 and not any((q.must, q.must_not, q.filter)):
                other = self if q is other else other
                q = q._clone()
                q.should.append(other)
                return q

        return Bool(should=[self, other])
    __ror__ = __or__

    def __invert__(self):
        # special case for single negated query
        if not (self.must or self.should or self.filter) and len(self.must_not) == 1:
            return self.must_not[0]._clone()

        # bol without should, just flip must and must_not
        elif not self.should:
            q = self._clone()
            q.must, q.must_not = q.must_not, q.must
            if q.filter:
                q.filter = [Bool(must_not=q.filter)]
            return q

        # TODO: should -> must_not.append(Bool(should=self.should)) ??
        # queries with should just invert normally
        return super(Bool, self).__invert__()

    def __and__(self, other):
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.must_not += other.must_not
            q.filter += other.filter
            q.should = []
            for qx in (self, other):
                # TODO: percetages will fail here
                min_should_match = getattr(qx, 'minimum_should_match', 0 if qx.must else 1)
                # all subqueries are required
                if len(qx.should) <= min_should_match:
                    q.must.extend(qx.should)
                # not all of them are required, use it and remember min_should_match
                elif not q.should:
                    q.minimum_should_match = min_should_match
                    q.should = qx.should
                # not all are required, add a should list to the must with proper min_should_match
                else:
                    q.must.append(Bool(should=qx.should, minimum_should_match=min_should_match))
        else:
            q.must.append(other)
        return q
    __rand__ = __and__

class FunctionScore(Query):
    name = 'function_score'
    _param_defs = {
        'query': {'type': 'query'},
        'filter': {'type': 'query'},
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
    ('constant_score', {'query': {'type': 'query'}, 'filter': {'type': 'query'}}),
    ('dis_max', {'queries': {'type': 'query', 'multi': True}}),
    ('filtered', {'query': {'type': 'query'}, 'filter': {'type': 'query'}}),
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
    ('geo_bounding_box', None),
    ('geo_distance', None),
    ('geo_distance_range', None),
    ('geo_polygon', None),
    ('geo_shape', None),
    ('geohash_cell', None),
    ('ids', None),
    ('limit', None),
    ('match', None),
    ('match_phrase', None),
    ('match_phrase_prefix', None),
    ('exists', None),
    ('missing', None),
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
    ('script', None),
    ('type', None),
)

# generate the query classes dynamicaly
for qname, params_def in QUERIES:
    qclass = _make_dsl_class(Query, qname, params_def)
    globals()[qclass.__name__] = qclass

