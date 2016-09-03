from ..utils import AttrDict, AttrList

from .hit import Hit, HitMeta

class SuggestResponse(AttrDict):
    def success(self):
        return not self._shards.failed

class Response(AttrDict):
    def __init__(self, response, callbacks=None):
        super(AttrDict, self).__setattr__('_callbacks', callbacks or {})
        super(Response, self).__init__(response)

    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        # for slicing etc
        return self.hits[key]

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
            hit['inner_hits'][t] = Response(hit['inner_hits'][t], callbacks=self._callbacks)
        return self._callbacks.get(dt, Hit)(hit)

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
