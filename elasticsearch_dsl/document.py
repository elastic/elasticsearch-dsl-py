import re

from six import iteritems, add_metaclass

from .field import FieldBase
from .mapping import Mapping
from .utils import ObjectBase

class DocTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        # DocTypeMeta filters attrs in place
        attrs['_meta'] = DocTypeOptions(name, bases, attrs)
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)


class DocTypeOptions(object):
    def __init__(self, name, bases, attrs):
        meta = attrs.pop('Meta', None)

        doc_type = getattr(meta, 'doc_type', re.sub(r'(.)([A-Z])', r'\1_\2', name).lower())
        self.mapping = getattr(meta, 'mapping', Mapping(doc_type))

        for name, value in list(iteritems(attrs)):
            if isinstance(value, FieldBase):
                self.mapping.field(name, value)
                del attrs[name]

        # document inheritance
        for b in bases:
            if hasattr(b, '_meta') and hasattr(b._meta, 'mapping'):
                self.mapping.update(b._meta.mapping, update_only=True)

    @property
    def doc_type(self):
        return self.mapping.properties.name


@add_metaclass(DocTypeMeta)
class DocType(ObjectBase):
    pass
