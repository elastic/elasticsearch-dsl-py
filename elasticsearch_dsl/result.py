from six import iteritems, u

from .utils import AttrDict, AttrList

class ResultMeta(AttrDict):
    def __init__(self, document):
        d = dict((k[1:], v) for (k, v) in iteritems(document) if k.startswith('_') and k != '_source')
        # make sure we are consistent everywhere in python
        d['doc_type'] = d['type']
        super(ResultMeta, self).__init__(d)

class Result(AttrDict):
    def __init__(self, document):
        if 'fields' in document:
            super(Result, self).__init__(document['fields'])
        else:
            super(Result, self).__init__(document['_source'])
        # assign _meta as attribute and not as key in self._d_
        super(AttrDict, self).__setattr__('_meta', ResultMeta(document))

    def __dir__(self):
        # be sure to expose _meta in dir(self)
        return super(Result, self).__dir__() + ['_meta']

    def __repr__(self):
        return u('<%s(%s/%s/%s): %s>') % (
            self.__class__.__name__, self._meta.index, self._meta.doc_type, self._meta.id,
            super(Result, self).__repr__())

class Response(AttrDict):
    result_factory = Result

    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        # for slicing etc
        return self.hits[key]

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.hits)

    def success(self):
        return not (self.timed_out or self._shards.failed)

    @property
    def hits(self):
        if not hasattr(self, '_hits'):
            h = self._d_['hits']
            # avoid assigning _hits into self._d_
            super(AttrDict, self).__setattr__('_hits', AttrList(map(self.result_factory, h['hits'])))
            for k in h:
                setattr(self._hits, k, h[k])
        return self._hits
