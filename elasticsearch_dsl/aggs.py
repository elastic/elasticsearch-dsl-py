from six import add_metaclass

from .utils import DslMeta

class BucketMeta(DslMeta):
    _classes = {}

def A(name_or_agg, agg_type=None, **params):
    if isinstance(name_or_agg, dict):
        if params or agg_type or len(name_or_agg) != 1:
            raise #XXX
        name, agg = name_or_agg.popitem()
        aggs = agg.pop('aggs', None)
        if len(agg) != 1:
            raise #XXX
        agg_type, params = agg.popitem()
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

@add_metaclass(BucketMeta)
class Agg(object):
    name = None
    def __init__(self, name, **params):
        self._name = name
        self._params = params

    def __eq__(self, other):
        return isinstance(other, Agg) and other.name == self.name \
            and other._name == self._name and other._params == self._params

    def to_dict(self):
        return {
            self._name: {
                self.name: self._params
            }
        }

class Bucket(Agg):
    def __init__(self, name, aggs=None, **params):
        super(Bucket, self).__init__(name, **params)
        self.aggs = {}
        if aggs:
            for name, agg in aggs.items():
                self[name] = {name: agg}

    def __eq__(self, other):
        return super(Bucket, self).__eq__(other) and self.aggs == other.aggs

    def __getitem__(self, agg_name):
        return self.aggs[agg_name] # propagate KeyError

    def __setitem__(self, agg_name, agg):
        self.aggs[agg_name] = A(agg)

    def _agg(self, bucket, name, agg_type, **params):
        agg = self.aggs[name] = A(name, agg_type, **params)
        # when creating new buckets return them...
        if bucket:
            return agg

        # otherwise return self so we can keep chaining
        else:
            return self

    def aggregate(self, name, agg_type, **params):
        return self._agg(False, name, agg_type, **params)

    def bucket(self, name, agg_type, **params):
        return self._agg(True, name, agg_type, **params)

    def to_dict(self):
        d =  {
            self._name: {
                self.name: self._params
            }
        }
        if self.aggs:
            aggs = {}
            d[self._name]['aggs'] = aggs
            for a in self.aggs.values():
                aggs.update(a.to_dict())
        return d

class Terms(Bucket):
    name = 'terms'

class Max(Agg):
    name = 'max'
