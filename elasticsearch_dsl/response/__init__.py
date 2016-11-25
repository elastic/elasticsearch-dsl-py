from ..utils import AttrDict, AttrList

from .hit import Hit, HitMeta
from .aggs import AggResponse

class SuggestResponse(AttrDict):
    def success(self):
        return not self._shards.failed

class Response(AttrDict):
    def __init__(self, search, response):
        super(AttrDict, self).__setattr__('_search', search)
        super(Response, self).__init__(response)

    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        if isinstance(key, (slice, int)):
            # for slicing etc
            return self.hits[key]
        return super(Response, self).__getitem__(key)

    def __nonzero__(self):
        return bool(self.hits)
    __bool__ = __nonzero__

    def __repr__(self):
        return '<Response: %r>' % self.hits

    def __len__(self):
        return len(self.hits)

    def success(self):
        return self._shards.total == self._shards.successful and not self.timed_out

    def _get_result(self, hit):
        dt = hit['_type']
        for t in hit.get('inner_hits', ()):
            hit['inner_hits'][t] = Response(self._search, hit['inner_hits'][t])
        return self._search._doc_type_map.get(dt, Hit)(hit)

    @property
    def hits(self):
        if not hasattr(self, '_hits'):
            h = self._d_['hits']

            try:
                hits = AttrList(map(self._get_result, h['hits']))
            except AttributeError as e:
                # avoid raising AttributeError since it will be hidden by the property
                raise TypeError("Could not parse hits.", e)

            # avoid assigning _hits into self._d_
            super(AttrDict, self).__setattr__('_hits', hits)
            for k in h:
                setattr(self._hits, k, h[k])
        return self._hits

    @property
    def aggregations(self):
        return self.aggs

    @property
    def aggs(self):
        if not hasattr(self, '_aggs'):
            aggs = AggResponse(self._search.aggs, self._d_.get('aggregations', {}))

            # avoid assigning _aggs into self._d_
            super(AttrDict, self).__setattr__('_aggs', aggs)
        return self._aggs
