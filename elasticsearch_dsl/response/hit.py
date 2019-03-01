from ..utils import AttrDict, HitMeta

class Hit(AttrDict):
    def __init__(self, document):
        data = {}
        if '_source' in document:
            data = document['_source']
        if 'fields' in document:
            data.update(document['fields'])

        super(Hit, self).__init__(data)
        # assign meta as attribute and not as key in self._d_
        super(AttrDict, self).__setattr__('meta', HitMeta(document))

    def __getstate__(self):
        # add self.meta since it is not in self.__dict__
        return super(Hit, self).__getstate__() + (self.meta, )

    def __setstate__(self, state):
        super(AttrDict, self).__setattr__('meta', state[-1])
        super(Hit, self).__setstate__(state[:-1])

    def __dir__(self):
        # be sure to expose meta in dir(self)
        return super(Hit, self).__dir__() + ['meta']

    def __repr__(self):
        return '<Hit(%s): %s>' % (
            '/'.join(
                getattr(self.meta, key)
                for key in ('index', 'doc_type', 'id')
                if key in self.meta),
            super(Hit, self).__repr__()
        )
