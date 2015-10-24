from collections import namedtuple
from datetime import datetime, timedelta
from .utils import DslBase, _make_dsl_class
from .filter import F

__all__ = [
    'A', 'Agg', 'Filter', 'Bucket', 'Children', 'DateHistogram', 'Filters',
    'GeoDistance', 'GeohashGrid', 'Global', 'Histogram', 'Iprange', 'Missing',
    'Nested', 'Range', 'ReverseNested', 'SignificantTerms', 'Terms', 'Avg',
    'Cardinality', 'ExtendedStats', 'GeoBounds', 'Max', 'Min', 'Percentiles',
    'PercenileRanks', 'ScriptedMetric', 'Stats', 'Sum', 'TopHits', 'ValueCount'
]


def A(name_or_agg, filter=None, **params):
    if filter is not None:
        if name_or_agg != 'filter':
            raise ValueError("Aggregation %r doesn't accept positional argument 'filter'." % name_or_agg)
        params['filter'] = filter

    # {"terms": {"field": "tags"}, "aggs": {...}}
    if isinstance(name_or_agg, dict):
        if params:
            raise ValueError('A() cannot accept parameters when passing in a dict.')
        # copy to avoid modifying in-place
        agg = name_or_agg.copy()
        # pop out nested aggs
        aggs = agg.pop('aggs', None)
        # should be {"terms": {"fied": "tags"}}
        if len(agg) != 1:
            raise ValueError('A() can only accept dict with an aggregation ({"terms": {...}}). '
                 'Instead it got (%r)' % name_or_agg)
        agg_type, params = agg.popitem()
        if aggs:
            params = params.copy()
            params['aggs'] = aggs
        return Agg.get_dsl_class(agg_type)(**params)

    # Terms(...) just return the nested agg
    elif isinstance(name_or_agg, Agg):
        if params:
            raise ValueError('A() cannot accept parameters when passing in an Agg object.')
        return name_or_agg

    # "terms", field="tags"
    return Agg.get_dsl_class(name_or_agg)(**params)

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

    def _agg(self, bucket, name, agg_type, *args,**params):
        agg = self[name] = A(agg_type, *args, **params)

        # For chaining - when creating new buckets return them...
        if bucket:
            return agg
        # otherwise return self._base so we can keep chaining
        else:
            return self._base

    def metric(self, name, agg_type, *args, **params):
        return self._agg(False, name, agg_type, *args, **params)

    def bucket(self, name, agg_type, *args, **params):
        return self._agg(True, name, agg_type, *args, **params)

    def to_filter(self, value):
        raise NotImplementedError()

    def to_python(self, bucket, bucket_filter):
        raise NotImplementedError()


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


class Filter(Bucket):
    name = 'filter'
    _param_defs = {
        'filter': {'type': 'filter'},
        'aggs': {'type': 'agg', 'hash': True},
    }

    def __init__(self, filter=None, **params):
        if filter is not None:
            params['filter'] = filter
        super(Filter, self).__init__(**params)

    def to_dict(self):
        d = super(Filter, self).to_dict()
        d[self.name].update(d[self.name].pop('filter', {}))
        return d


FacetResults = namedtuple('FacetResults', 'value doc_count is_active')


class Terms(Bucket):
    name = 'terms'

    def to_filter(self, value):
        return F('term', **{self.field: value})

    def to_python(self, bucket, bucket_filter):
        return FacetResults(bucket['key'], bucket['doc_count'],
                            bucket['key'] in bucket_filter)


class Histogram(Bucket):
    name = 'histogram'

    def to_filter(self, value):
        filter_body = {'gte': value, 'lt': value+self.interval}
        return F('range', **{self.field: filter_body})


class DateHistogram(Bucket):
    DATE_INTERVALS = {
        'month': lambda d: (d+timedelta(days=32)).replace(day=1),
        'week': lambda d: d+timedelta(days=7),
        'day': lambda d: d+timedelta(days=1),
        'hour': lambda d: d+timedelta(hours=1),
    }
    name = 'date_histogram'

    def to_filter(self, value):
        filter_body = {
            'gte': value,
            'lt': self.DATE_INTERVALS[self.interval](value)
        }
        return F('range', **{self.field: filter_body})

    def to_python(self, bucket, bucket_filter):
        d = datetime.utcfromtimestamp(int(bucket['key']) / 1000)
        return FacetResults(d, bucket['doc_count'], d in bucket_filter)

AGGS = (
    (Bucket, 'children', None),
    (Bucket, 'date_range', None),
    (Bucket, 'filters', {'filters': {'type': 'filter', 'hash': True}}),
    (Bucket, 'geo_distance', None),
    (Bucket, 'geohash_grid', None),
    (Bucket, 'global', None),
    (Bucket, 'iprange', None),
    (Bucket, 'missing', None),
    (Bucket, 'nested', None),
    (Bucket, 'range', None),
    (Bucket, 'reverse_nested', None),
    (Bucket, 'significant_terms', None),

    (Agg, 'avg', None),
    (Agg, 'cardinality', None),
    (Agg, 'extended_stats', None),
    (Agg, 'geo_bounds', None),
    (Agg, 'max', None),
    (Agg, 'min', None),
    (Agg, 'percentiles', None),
    (Agg, 'percentile_ranks', None),
    (Agg, 'scripted_metric', None),
    (Agg, 'stats', None),
    (Agg, 'sum', None),
    (Agg, 'top_hits', None),
    (Agg, 'value_count', None),
)

# generate the aggregation classes dynamicaly
for base, fname, params_def in AGGS:
    # don't override the params def from AggBase
    if params_def:
        params_def.update(AggBase._param_defs)
    fclass = _make_dsl_class(base, fname, params_def)
    globals()[fclass.__name__] = fclass

