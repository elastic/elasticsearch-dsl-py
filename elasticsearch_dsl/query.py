class Query(object):
    name = None
    def __init__(self, **params):
        self._params = params

    def __add__(self, other):
        return BoolQuery(must=[self, other])

    def to_dict(self):
        return {self.name: self._params}

class MatchQuery(Query):
    name = 'match'

class BoolQuery(Query):
    name = 'bool'

    @property
    def must(self):
        return self._params.setdefault('must', [])

    @property
    def should(self):
        return self._params.setdefault('should', [])

    @property
    def must_not(self):
        return self._params.setdefault('must_not', [])

    def to_dict(self):
        d = {}
        out = {self.name: d}
        for n in ('must', 'should', 'must_not'):
            if n in self._params:
                d[n] = list(map(lambda x: x.to_dict(), self._params[n]))
        return out
