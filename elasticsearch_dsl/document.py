import re

from six import iteritems, add_metaclass

from .field import FieldBase
from .mapping import Mapping
from .utils import ObjectBase, AttrDict
from .result import ResultMeta
from .search import Search
from .connections import connections

META_FIELDS = frozenset((
    # Elasticsearch metadata fields, except 'type'
    'id', 'index', 'parent', 'percolate', 'routing', 'timestamp', 'ttl',
    'version', 'version_type',
))

class DocTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        # DocTypeMeta filters attrs in place
        attrs['_doc_type'] = DocTypeOptions(name, bases, attrs)
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)


class DocTypeOptions(object):
    def __init__(self, name, bases, attrs):
        meta = attrs.pop('Meta', None)

        # default index, if not overriden by doc._meta
        self.index = getattr(meta, 'index', None)

        # default cluster alias, can be overriden in doc._meta
        self.using = getattr(meta, 'using', 'default')

        # get doc_type name, if not defined take the name of the class and
        # tranform it to lower_case
        doc_type = getattr(meta, 'doc_type',
                re.sub(r'(.)([A-Z])', r'\1_\2', name).lower())

        # create the mapping instance
        self.mapping = getattr(meta, 'mapping', Mapping(doc_type))

        # register all declared fields into the mapping
        for name, value in list(iteritems(attrs)):
            if isinstance(value, FieldBase):
                self.mapping.field(name, value)
                del attrs[name]

        # document inheritance - include the fields from parents' mappings
        for b in bases:
            if hasattr(b, '_doc_type') and hasattr(b._doc_type, 'mapping'):
                self.mapping.update(b._doc_type.mapping, update_only=True)

    @property
    def name(self):
        return self.mapping.properties.name


@add_metaclass(DocTypeMeta)
class DocType(ObjectBase):
    def __init__(self, **kwargs):
        meta = {}
        for k in list(kwargs):
            if k.startswith('_'):
                meta[k] = kwargs.pop(k)
        super(AttrDict, self).__setattr__('_meta', ResultMeta(meta))

        super(DocType, self).__init__(**kwargs)

    @classmethod
    def search(cls):
        #TODO: register callback for doc_type
        return Search(using=cls._doc_type.using, doc_type=cls._doc_type.name, index=cls._doc_type.index)

    @classmethod
    def get(cls, id, using=None, index=None, **kwargs):
        es = connections.get_connection(using or cls._doc_type.using)
        doc = es.get(
            index=index or cls._doc_type.index,
            doc_type=cls._doc_type.name,
            id=id,
            **kwargs
        )
        return cls.from_es(doc)

    @classmethod
    def from_es(cls, hit):
        # don't modify in place
        doc = hit.copy()
        doc.update(doc.pop('_source'))
        return cls(**doc)

    def _get_connection(self, using=None):
        if using:
            return connections.get_connection(using)
        return connections.get_connection(getattr(self._meta, 'using', self._doc_type.using))

    def save(self, using=None, index=None, **kwargs):
        es = self._get_connection(using)
        if index is None:
            index = getattr(self._meta, 'index', self._doc_type.index)
        if index is None:
            raise #XXX - no index
        meta = es.index(
            index=index,
            doc_type=self._doc_type.name,
            id=getattr(self, 'id', None),
            body=self.to_dict(),
            **kwargs
        )
        # update meta information from ES
        for k in META_FIELDS:
            if '_' + k in meta:
                setattr(self, k, meta['_' + k])

        # return True/False if the document has been created/updated
        return meta['created']

    def __getattr__(self, name):
        if name in META_FIELDS:
            try:
                return getattr(self._meta, name)
            except AttributeError:
                return getattr(self._doc_type, name)
        return super(DocType, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name in META_FIELDS:
            return setattr(self._meta, name, value)
        return super(DocType, self).__setattr__(name, value)

