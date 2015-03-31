from .utils import DslBase, BoolMixin, _make_dsl_class

def F(name_or_filter, filters=None, **params):
    # 'and/or', [F(), F()]
    if filters is not None:
        # someone passed in positional argument to F outside of and/or
        if name_or_filter not in ('and', 'or'):
            raise ValueError("Filter %r doesn't accept positional argument 'filters'." % name_or_filter)
        params['filters'] = filters

    # {"term": {...}}
    if isinstance(name_or_filter, dict):
        if params:
            raise ValueError('F() cannot accept parameters when passing in a dict.')
        if len(name_or_filter) != 1:
            raise ValueError('F() can only accept dict with a single filter ({"bool": {...}}). '
                 'Instead it got (%r)' % name_or_filter)
        name, params = name_or_filter.copy().popitem()
        return Filter.get_dsl_class(name)(**params)

    # Term(...)
    if isinstance(name_or_filter, Filter):
        if params:
            raise ValueError('F() cannot accept parameters when passing in a Filter object.')
        return name_or_filter

    # s.filter = ~F(s.filter)
    if hasattr(name_or_filter, '_proxied'):
        return name_or_filter._proxied

    # 'term', tag='python', ...
    return Filter.get_dsl_class(name_or_filter)(**params)

class Filter(DslBase):
    _type_name = 'filter'
    _type_shortcut = staticmethod(F)
    name = None

class MatchAll(Filter):
    name = 'match_all'
    def __add__(self, other):
        return other._clone()
    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other):
        return self
    __ror__ = __or__
EMPTY_FILTER = MatchAll()

class Bool(BoolMixin, Filter):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'filter', 'multi': True},
        'should': {'type': 'filter', 'multi': True},
        'must_not': {'type': 'filter', 'multi': True},
    }
# register this as Bool for Filter
Filter._bool = Bool

class Not(Filter):
    name = 'not'
    _param_defs = {'filter': {'type': 'filter'}}

    def __init__(self, filter=None, **kwargs):
        if filter is None:
            filter, kwargs = kwargs, {}
        super(Not, self).__init__(filter=filter, **kwargs)

class AndOrFilter(object):
    _param_defs = {'filters': {'type': 'filter', 'multi': True}}

    def __init__(self, filters=None, **kwargs):
        if filters is not None:
            kwargs['filters'] = filters
        super(AndOrFilter, self).__init__(**kwargs)

    # compound filters
class And(AndOrFilter, Filter):
    name = 'and'

class Or(AndOrFilter, Filter):
    name = 'or'

FILTERS = (
    # relationships
    ('nested', {'filter': {'type': 'filter'}}),
    ('has_child', {'filter': {'type': 'filter'}}),
    ('has_parent', {'filter': {'type': 'filter'}}),

    ('fquery', {'query': {'type': 'query'}}),

    # core filters
    ('exists', None),
    ('geo_bounding_box', None),
    ('geo_distance', None),
    ('geo_distance_range', None),
    ('geo_polygon', None),
    ('geo_shape', None),
    ('geohash_cell', None),
    ('ids', None),
    ('indices', None),
    ('limit', None),
    ('missing', None),
    ('prefix', None),
    ('range', None),
    ('regexp', None),
    ('script', None),
    ('term', None),
    ('terms', None),
    ('type', None),
)

# generate the filter classes dynamicaly
for fname, params_def in FILTERS:
    fclass = _make_dsl_class(Filter, fname, params_def)
    globals()[fclass.__name__] = fclass

