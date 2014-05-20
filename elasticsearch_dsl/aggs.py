from six import add_metaclass, iteritems

from .utils import DslMeta, DslBase

class AggMeta(DslMeta):
    _classes = {}

def A(name_or_agg, agg_type=None, **params):
    if isinstance(name_or_agg, dict):
        if params or agg_type or len(name_or_agg) != 1:
            raise #XXX
        name, agg = name_or_agg.copy().popitem()
        if isinstance(agg, Agg):
            return agg
        agg = agg.copy()
        aggs = agg.pop('aggs', None)
        if len(agg) != 1:
            raise #XXX
        agg_type, params = agg.copy().popitem()
        if aggs:
            params = params.copy()
            params['aggs'] = aggs
        return Agg.get_dsl_class(agg_type)(name, **params)
    elif isinstance(name_or_agg, Agg):
        if params or agg_type:
            raise #XXX
        return name_or_agg
    elif agg_type is None:
        raise #XXX
    
    return Agg.get_dsl_class(agg_type)(name_or_agg, **params)

@add_metaclass(AggMeta)
class Agg(DslBase):
    _type_name = 'agg'
    _type_shortcut = staticmethod(A)
    name = None

    def __init__(self, name, **params):
        self._name = name
        super(Agg, self).__init__(**params)

    def to_dict(self):
        d = super(Agg, self).to_dict()
        out = {self._name: d}
        if 'aggs' in d[self.name]:
            d['aggs'] = d[self.name].pop('aggs')

        return out

class AggBase(object):
    _param_defs = {
        'aggs': {'type': 'agg', 'hash': True},
    }
    def __getitem__(self, agg_name):
        agg = self._params.setdefault('aggs', {})[agg_name] # propagate KeyError
        # make sure we're not mutating a shared state - whenever accessing a
        # bucket, return a shallow copy of it to be safe
        if isinstance(agg, Bucket):
            agg = A(agg_name, agg.name, **agg._params)
            self._params['aggs'][agg_name] = agg

        return agg

    def __setitem__(self, agg_name, agg):
        self.aggs[agg_name] = A(agg)

    def _agg(self, bucket, name, agg_type, **params):
        agg = self[name] = A(name, agg_type, **params)
        # when creating new buckets return them...
        if bucket:
            return agg

        # otherwise return self._base so we can keep chaining
        else:
            return self._base

    def aggregate(self, name, agg_type, **params):
        return self._agg(False, name, agg_type, **params)

    def bucket(self, name, agg_type, **params):
        return self._agg(True, name, agg_type, **params)


class Bucket(AggBase, Agg):
    def __init__(self, name, **params):
        super(Bucket, self).__init__(name, **params)
        self._base = self

class Terms(Bucket):
    name = 'terms'

class DateHistogram(Bucket):
    name = 'date_histogram'

class Max(Agg):
    name = 'max'

class Avg(Agg):
    name = 'avg'
