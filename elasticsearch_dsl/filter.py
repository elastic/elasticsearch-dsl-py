from six import add_metaclass

from .utils import DslMeta, DslBase, BoolMixin

class FilterMeta(DslMeta):
    _classes = {}

def F(name_or_filter, **params):
    if isinstance(name_or_filter, dict):
        if params:
            raise #XXX
        if len(name_or_filter) != 1:
            raise #XXX
        name, params = name_or_filter.popitem()
        return Filter.get_dsl_class(name)(**params)
    if isinstance(name_or_filter, Filter):
        if params:
            raise #XXX
        return name_or_filter
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

class Bool(BoolMixin, Filter):
    name = 'bool'
    _param_defs = {
        'must': {'type': 'filter', 'multi': True},
        'should': {'type': 'filter', 'multi': True},
        'must_not': {'type': 'filter', 'multi': True},
    }

# register this as Bool for Filter
Filter._bool = Bool

EMPTY_FILTER = Bool()
