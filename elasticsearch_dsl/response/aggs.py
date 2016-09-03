from ..utils import AttrDict

class AggResponse(AttrDict):
    def __init__(self, aggs, data):
        super(AttrDict, self).__setattr__('_aggs', aggs)
        super(AggResponse, self).__init__(data)

    def __getitem__(self, attr_name):
        if attr_name in self._aggs:
            # don't do self._aggs[attr_name] to avoid copying
            agg = self._aggs.aggs[attr_name]
            return agg.result(self._d_[attr_name])
        return super(AggResponse, self).__getitem__(attr_name)

    def __iter__(self):
        for name in self._aggs:
            yield self[name]

class AggData(AttrDict):
    def __init__(self, agg, data):
        super(AggData, self).__init__(data)
        super(AttrDict, self).__setattr__('meta', AttrDict({'agg': agg}))

class BucketData(AggData):
    pass
