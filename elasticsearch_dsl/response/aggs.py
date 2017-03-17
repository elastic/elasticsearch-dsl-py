from ..utils import AttrDict
from . import Response, AggResponse

def _resolve_field(search, field):
    for dt in search._doc_type_map.values():
        f = dt._doc_type.resolve_field(field)
        if f:
            return f

class Bucket(AggResponse):
    def __init__(self, aggs, search, data, field=None):
        if field:
            data['key'] = field.deserialize(data['key'])
        super(Bucket, self).__init__(aggs, search, data)

class BucketData(AggResponse):
    _bucket_class = Bucket
    def _wrap_bucket(self, data, field=None):
        return self._bucket_class(self._meta['aggs'], self._meta['search'], data, field=field)

    def __iter__(self):
        return iter(self.buckets)

    def __len__(self):
        return len(self.buckets)

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self.buckets[key]
        return super(BucketData, self).__getitem__(key)

    @property
    def buckets(self):
        if not hasattr(self, '_buckets'):
            field = getattr(self._meta['aggs'], 'field', None)
            if field:
                field = _resolve_field(self._meta['search'], field)
            bs = [self._wrap_bucket(b, field=field) for b in self._d_['buckets']]
            super(AttrDict, self).__setattr__('_buckets', bs)
        return self._buckets

class TopHitsData(Response):
    def __init__(self, agg, search, data):
        super(AttrDict, self).__setattr__('meta', AttrDict({'agg': agg, 'search': search}))
        super(TopHitsData, self).__init__(search, data)
