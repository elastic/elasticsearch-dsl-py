from six import add_metaclass

from .utils import DslMeta, DslBase, _make_dsl_class

class AggMeta(DslMeta):
    _classes = {}

def A(name_or_agg, **params):
    # {"terms": {"field": "tags"}, "aggs": {...}}
    if isinstance(name_or_agg, dict):
        if params:
            raise #XXX
        # copy to avoid modifying in-place
        agg = name_or_agg.copy()
        # pop out nested aggs
        aggs = agg.pop('aggs', None)
        # should be {"terms": {"fied": "tags"}}
        if len(agg) != 1:
            raise #XXX
        agg_type, params = agg.popitem()
        if aggs:
            params = params.copy()
            params['aggs'] = aggs
        return Agg.get_dsl_class(agg_type)(**params)

    # Terms(...) just return the nested agg
    elif isinstance(name_or_agg, Agg):
        if params:
            raise #XXX
        return name_or_agg

    # "terms", field="tags"
    return Agg.get_dsl_class(name_or_agg)(**params)

@add_metaclass(AggMeta)
class Agg(DslBase):
    _type_name = 'agg'
    _type_shortcut = staticmethod(A)
    name = None

class AggBase(object):
    _param_defs = {
        'aggs': {'type': 'agg', 'hash': True},
    }
    def __getitem__(self, agg_name):
        agg = self._params.setdefault('aggs', {})[agg_name] # propagate KeyError

        # make sure we're not mutating a shared state - whenever accessing a
        # bucket, return a shallow copy of it to be safe
        if isinstance(agg, Bucket):
            agg = A(agg.name, **agg._params)
            # be sure to store the copy so any modifications to it will affect us
            self._params['aggs'][agg_name] = agg

        return agg

    def __setitem__(self, agg_name, agg):
        self.aggs[agg_name] = A(agg)

    def _agg(self, bucket, name, agg_type, **params):
        agg = self[name] = A(agg_type, **params)

        # For chaining - when creating new buckets return them...
        if bucket:
            return agg
        # otherwise return self._base so we can keep chaining
        else:
            return self._base

    def metric(self, name, agg_type, **params):
        return self._agg(False, name, agg_type, **params)

    def bucket(self, name, agg_type, **params):
        return self._agg(True, name, agg_type, **params)


class Bucket(AggBase, Agg):
    def __init__(self, **params):
        super(Bucket, self).__init__(**params)
        # remember self for chaining
        self._base = self

    def to_dict(self):
        d = super(AggBase, self).to_dict()
        if 'aggs' in d[self.name]:
            d['aggs'] = d[self.name].pop('aggs')
        return d

AGGS = (
    (Bucket, 'children', None),
    (Bucket, 'date_histogram', None),
    (Bucket, 'date_range', None),
    (Bucket, 'filter', {'filter': {'type': 'filter'}}),
    (Bucket, 'filters', {'filters': {'type': 'filter', 'hash': True}}),
    (Bucket, 'geo_distance', None),
    (Bucket, 'geo_hashgrid', None),
    (Bucket, 'global', None),
    (Bucket, 'histogram', None),
    (Bucket, 'iprange', None),
    (Bucket, 'missing', None),
    (Bucket, 'nested', None),
    (Bucket, 'range', None),
    (Bucket, 'reverse_nested', None),
    (Bucket, 'significant_terms', None),
    (Bucket, 'terms', None),

    (Agg, 'avg', None),
    (Agg, 'cardinality', None),
    (Agg, 'extended_stats', None),
    (Agg, 'geo_bounds', None),
    (Agg, 'max', None),
    (Agg, 'min', None),
    (Agg, 'percentile', None),
    (Agg, 'percentile_rank', None),
    (Agg, 'scripted_metric', None),
    (Agg, 'stats', None),
    (Agg, 'sum', None),
    (Agg, 'top_hits', None),
    (Agg, 'value_count', None),
)

# generate the filter classes dynamicaly
for base, fname, params_def in AGGS:
    # don't override the params def from AggBase
    if params_def:
        params_def.update(AggBase._param_defs)
    fclass = _make_dsl_class(base, fname, params_def)
    globals()[fclass.__name__] = fclass
