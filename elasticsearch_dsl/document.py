import re

from six import iteritems, add_metaclass

from .field import Field
from .mapping import Mapping
from .utils import ObjectBase, AttrDict
from .result import ResultMeta
from .search import Search
from .connections import connections

DOC_META_FIELDS = frozenset((
    'id', 'parent', 'routing', 'timestamp', 'ttl', 'version', 'version_type'
))

META_FIELDS = frozenset((
    # Elasticsearch metadata fields, except 'type'
    'index', 'using', 'score',
)).union(DOC_META_FIELDS)

class MetaField(dict):
    pass

class DocTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        # DocTypeMeta filters attrs in place
        attrs['_doc_type'] = DocTypeOptions(name, bases, attrs)
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)

class DocTypeOptions(object):
    def __init__(self, name, bases, attrs):
        meta = attrs.pop('Meta', None)

        # default index, if not overriden by doc.meta
        self.index = getattr(meta, 'index', None)

        # default cluster alias, can be overriden in doc.meta
        self._using = getattr(meta, 'using', None)

        # get doc_type name, if not defined take the name of the class and
        # tranform it to lower_case
        doc_type = getattr(meta, 'doc_type',
                re.sub(r'(.)([A-Z])', r'\1_\2', name).lower())

        # create the mapping instance
        self.mapping = getattr(meta, 'mapping', Mapping(doc_type))

        # register all declared fields into the mapping
        for name, value in list(iteritems(attrs)):
            if isinstance(value, Field):
                self.mapping.field(name, value)
                del attrs[name]

        # add all the mappings for meta fields
        for name in dir(meta):
            if isinstance(getattr(meta, name, None), MetaField):
                self.mapping.meta('_' + name if not name.startswith('_') else name, **getattr(meta, name))

        # document inheritance - include the fields from parents' mappings and
        # index/using values
        for b in bases:
            if hasattr(b, '_doc_type') and hasattr(b._doc_type, 'mapping'):
                self.mapping.update(b._doc_type.mapping, update_only=True)
                self._using = self._using or b._doc_type._using
                self.index = self.index or b._doc_type.index

    @property
    def using(self):
        return self._using or 'default'

    @property
    def name(self):
        return self.mapping.properties.name

    def init(self, index=None, using=None):
        self.mapping.save(index or self.index, using=using or self.using)

    def refresh(self, index=None, using=None):
        self.mapping.update_from_es(index or self.index, using=using or self.using)


@add_metaclass(DocTypeMeta)
class DocType(ObjectBase):
    def __init__(self, meta=None, **kwargs):
        meta = meta or {}
        for k in list(kwargs):
            if k.startswith('_'):
                meta[k] = kwargs.pop(k)
        super(AttrDict, self).__setattr__('meta', ResultMeta(meta))

        super(DocType, self).__init__(**kwargs)

    def __getattr__(self, name):
        if name.startswith('_') and name[1:] in META_FIELDS:
            return getattr(self.meta, name[1:])
        return super(DocType, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name.startswith('_') and name[1:] in META_FIELDS:
            return setattr(self.meta, name[1:], value)
        return super(DocType, self).__setattr__(name, value)

    @classmethod
    def init(cls, index=None, using=None):
        cls._doc_type.init(index, using)

    @classmethod
    def search(cls):
        return Search(
            using=cls._doc_type.using,
            index=cls._doc_type.index,
            doc_type={cls._doc_type.name: cls.from_es},
        )

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
        meta = hit.copy()
        doc = meta.pop('_source', {})

        if 'fields' in meta:
            for k, v in iteritems(meta.pop('fields')):
                if k == '_source':
                    doc.update(v)
                if k.startswith('_'):
                    meta[k] = v
                else:
                    doc[k] = v

        return cls(meta=meta, **doc)

    def _get_connection(self, using=None):
        return connections.get_connection(using or self._doc_type.using)
    connection = property(_get_connection)

    def delete(self, using=None, index=None, **kwargs):
        es = self._get_connection(using)
        if index is None:
            index = getattr(self.meta, 'index', self._doc_type.index)
        if index is None:
            raise #XXX - no index
        # extract parent, routing etc from meta
        doc_meta = dict((k, self.meta[k]) for k in DOC_META_FIELDS if k in self.meta)
        doc_meta.update(kwargs)
        es.delete(
            index=index,
            doc_type=self._doc_type.name,
            **doc_meta
        )

    def save(self, using=None, index=None, **kwargs):
        es = self._get_connection(using)
        if index is None:
            index = getattr(self.meta, 'index', self._doc_type.index)
        if index is None:
            raise #XXX - no index
        # extract parent, routing etc from meta
        doc_meta = dict((k, self.meta[k]) for k in DOC_META_FIELDS if k in self.meta)
        doc_meta.update(kwargs)
        meta = es.index(
            index=index,
            doc_type=self._doc_type.name,
            body=self.to_dict(),
            **doc_meta
        )
        # update meta information from ES
        for k in META_FIELDS:
            if '_' + k in meta:
                setattr(self.meta, k, meta['_' + k])

        # return True/False if the document has been created/updated
        return meta['created']

