from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin, _make_dsl_class

class FilterMeta(DslMeta):
    _classes = {}

def F(name_or_filter, filters=None, **params):
    # 'and/or', [F(), F()]
    if filters is not None:
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

    # 'term', tag='python', ...
    return Filter.get_dsl_class(name_or_filter)(**params)

@add_metaclass(FilterMeta)
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

    def __init__(self, **kwargs):
        if 'filter' not in kwargs:
            kwargs = {'filter': kwargs}
        super(Not, self).__init__(**kwargs)

FILTERS = (
    # compound filters
    ('and', {'filters': {'type': 'filter', 'multi': True}}),
    ('or', {'filters': {'type': 'filter', 'multi': True}}),

    # relationships
    ('nested', {'filter': {'type': 'filter'}}),
    ('has_child', {'filter': {'type': 'filter'}}),
    ('has_parent', {'filter': {'type': 'filter'}}),

    ('query', {'query': {'type': 'query'}}),

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

