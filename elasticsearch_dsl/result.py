from six import iteritems

class Hits(list):
    pass

class Response(object):
    def __init__(self, raw):
        self._response = raw
        self.took = raw['took']

    def success(self):
        return not (self._response['timed_out'] or self._response['_shards']['failed'])

    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        # for slicing etc
        return self.hits[key]

    @property
    def hits(self):
        if not hasattr(self, '_hits'):
            h = self._response['hits']
            self._hits = Hits(map(Result, h['hits']))
            self._hits.max_score = h['max_score']
            self._hits.total = h['total']
        return self._hits


class ResultMeta(object):
    def __init__(self, document):
        for k, v in iteritems(document):
            if k.startswith('_') and k != '_source':
                # make sure we are consistent everywhere in python
                if k == '_type':
                    self.doc_type = v
                setattr(self, k[1:], v)

class Result(object):
    def __init__(self, document):
        self._doc = document

    @property
    def _meta(self):
        if not hasattr(self, '__meta'):
            self.__meta = ResultMeta(self._doc)
        return self.__meta

    def __getattr__(self, attr_name):
        try:
            return self._doc['_source'][attr_name]
        except KeyError:
            raise AttributeError()
