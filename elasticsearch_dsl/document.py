import re

from six import iteritems, add_metaclass

from .field import FieldBase
from .mapping import Mapping
from .utils import ObjectBase, AttrDict
from .result import ResultMeta

META_FIELDS = frozenset((
    'id', 'index', 'parent', 'percolate', 'routing', 'timestamp', 'ttl', 'type',
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

        doc_type = getattr(meta, 'doc_type', re.sub(r'(.)([A-Z])', r'\1_\2', name).lower())
        self.mapping = getattr(meta, 'mapping', Mapping(doc_type))

        # default index, if not overriden by doc._meta
        self.index = getattr(meta, 'index', None)

        for name, value in list(iteritems(attrs)):
            if isinstance(value, FieldBase):
                self.mapping.field(name, value)
                del attrs[name]

        # document inheritance
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

