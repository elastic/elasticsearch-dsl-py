from ..utils import AttrDict, AttrList
from . import Response, AggResponse

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
class TopHitsData(Response):
    def __init__(self, agg, search, data):
        super(AttrDict, self).__setattr__('meta', AttrDict({'agg': agg, 'search': search}))
        super(TopHitsData, self).__init__(search, data)
