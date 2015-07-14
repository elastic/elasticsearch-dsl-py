from datetime import timedelta, datetime
from six import iteritems, itervalues
from functools import partial

from .search import Search
from .filter import F
from .aggs import Terms, DateHistogram, Histogram, Range
from .utils import AttrDict
from .result import Response

DATE_INTERVALS = {
    'month': lambda d: (d+timedelta(days=32)).replace(day=1),
    'week': lambda d: d+timedelta(days=7),
    'day': lambda d: d+timedelta(days=1),
    'hour': lambda d: d+timedelta(hours=1),

}

AGG_TO_FILTER = {
    Terms: lambda a, v: F('term', **{a.field: v}),
    DateHistogram: lambda a, v: F('range', **{a.field: {'gte': v, 'lt': DATE_INTERVALS[a.interval](v)}}),
    Histogram: lambda a, v:  F('range', **{a.field: {'gte': v, 'lt': v+a.interval}}),
    Range: lambda a, v: F('range', **{a.field: v})
}

BUCKET_TO_DATA = {
    Terms: lambda bucket, filter: (bucket['key'], bucket['doc_count'], bucket['key'] == filter),
    DateHistogram: lambda bucket, filter: (datetime.utcfromtimestamp(int(bucket['key']) / 1000), bucket['doc_count'], bucket['key'] == filter),
    Range: lambda bucket_key, bucket, filter: (bucket_key, bucket['doc_count'], bucket_key == filter)
}

def agg_to_filter(agg, value):
    return AGG_TO_FILTER[agg.__class__](agg, value)


class FacetedResponse(Response):
    def __init__(self, search, *args, **kwargs):
        super(FacetedResponse, self).__init__(*args, **kwargs)
        super(AttrDict, self).__setattr__('_search', search)

    @property
    def facets(self):
        if not hasattr(self, '_facets'):
            super(AttrDict, self).__setattr__('_facets', AttrDict({}))
            for name, agg in iteritems(self._search.facets):
                buckets = self._facets[name] = []
                data = self.aggregations['_filter_' + name][name]['buckets']
                filter = self._search._raw_filters.get(name, {})
                for b in data:
                    agg_class = agg.__class__
                    if agg_class == Range:
                        if getattr(agg, 'keyed', False):
                            bucket_key = b
                            bucket = data[b]
                            range_filter = filter
                        else:
                            bucket_key = b['key']
                            bucket = b
                            range_filter = '%s-%s' % (filter.get('from', '*'), filter.get('to', '*'))
                        buckets.append(BUCKET_TO_DATA[agg_class](bucket_key, bucket, range_filter))
                    else:
                        buckets.append(BUCKET_TO_DATA[agg.__class__](b, filter))
        return self._facets



class FacetedSearch(object):
    index = '_all'
    doc_types = ['_all']
    fields = ('*', )
    facets = {}

    def __init__(self, query=None, filters={}):
        self._query = query
        self._raw_filters = filters
        self._filters = {}
        for name, value in iteritems(filters):
            self.add_filter(name, value)

    def add_filter(self, name, value):
        agg = self.facets[name]
        if isinstance(value, list):
            self._filters[name] = F('bool', should=[agg_to_filter(agg, v) for v in value])
        else:
            self._filters[name] = agg_to_filter(agg, value)

    def search(self):
        return Search(doc_type=self.doc_types, index=self.index)

    def query(self, search):
        if self._query:
            return search.query('multi_match', fields=self.fields, query=self._query)
        return search

    def aggregate(self, search):
        for f, agg in iteritems(self.facets):
            agg_filter = F('match_all')
            for field, filter in iteritems(self._filters):
                if f == field:
                    continue
                agg_filter &= filter
            search.aggs.bucket(
                '_filter_' + f,
                'filter',
                filter=agg_filter
            ).bucket(f, agg)

    def filter(self, search):
        post_filter = F('match_all')
        for f in itervalues(self._filters):
            post_filter &= f
        return search.post_filter(post_filter)

    def build_search(self):
        s = self.search()
        s = self.query(s)
        self.aggregate(s)
        s = self.filter(s)
        return s

    def execute(self):
        if not hasattr(self, '_response'):
            s = self.build_search()
            self._response = s.execute(response_class=partial(FacetedResponse, self))

        return self._response

