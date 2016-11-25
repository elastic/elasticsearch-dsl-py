from ..utils import AttrDict, AttrList

class AggResponse(AttrDict):
    def __init__(self, aggs, search, data):
        super(AttrDict, self).__setattr__('_search', search)
        super(AttrDict, self).__setattr__('_aggs', aggs)
        super(AggResponse, self).__init__(data)

    def __getitem__(self, attr_name):
        if attr_name in self._aggs:
            # don't do self._aggs[attr_name] to avoid copying
            agg = self._aggs.aggs[attr_name]
            return agg.result(self._search, self._d_[attr_name])
        return super(AggResponse, self).__getitem__(attr_name)

    def __iter__(self):
        for name in self._aggs:
            yield self[name]

class AggData(AttrDict):
    def __init__(self, agg, search, data):
        super(AggData, self).__init__(data)
        super(AttrDict, self).__setattr__('meta', AttrDict({'agg': agg, 'search': search}))

class Bucket(AggResponse):
    pass

class BucketData(AggData):
    _bucket_class = Bucket
    def _wrap_bucket(self, data):
        return self._bucket_class(self.meta.agg, self.meta.search, data)

    @property
    def buckets(self):
        bs = self._d_['buckets']
        return AttrList(bs, self._wrap_bucket)
