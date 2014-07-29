from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin

class FilterMeta(DslMeta):
    _classes = {}

def F(name_or_filter, **params):
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

class Term(Filter):
    name = 'term'

class Terms(Filter):
    name = 'terms'

class Range(Filter):
    name = 'range'

class Missing(Filter):
    name = 'missing'

class Bool(BoolMixin, Filter):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'filter', 'multi': True},
        'should': {'type': 'filter', 'multi': True},
        'must_not': {'type': 'filter', 'multi': True},
    }

# register this as Bool for Filter
Filter._bool = Bool

class MatchAll(Filter):
    name = 'match_all'
    def __add__(self, other):
        return other._clone()
    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other):
        return self
    __ror__ = __or__

EMPTY_FILTER = MatchAll()
