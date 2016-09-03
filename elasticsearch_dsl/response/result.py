from six import iteritems

from ..utils import AttrDict

class ResultMeta(AttrDict):
    def __init__(self, document, exclude=('_source', '_fields')):
        d = dict((k[1:] if k.startswith('_') else k, v) for (k, v) in iteritems(document) if k not in exclude)
        if 'type' in d:
            # make sure we are consistent everywhere in python
            d['doc_type'] = d.pop('type')
        super(ResultMeta, self).__init__(d)

class Result(AttrDict):
    def __init__(self, document):
        data = {}
        if '_source' in document:
            data = document['_source']
        if 'fields' in document:
            data.update(document['fields'])

        super(Result, self).__init__(data)
        # assign meta as attribute and not as key in self._d_
        super(AttrDict, self).__setattr__('meta', ResultMeta(document))

    def __dir__(self):
        # be sure to expose meta in dir(self)
        return super(Result, self).__dir__() + ['meta']

    def __repr__(self):
        return '<Result(%s): %s>' % (
            '/'.join(getattr(self.meta, key) for key in
                      ('index', 'doc_type', 'id') if key in self.meta),
            super(Result, self).__repr__()
        )

