import re

from six import iteritems, add_metaclass

from .field import FieldBase
from .mapping import Mapping
from .utils import ObjectBase

class DocTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        doc_type = attrs.pop('doc_type', re.sub(r'(.)([A-Z])', r'\1_\2', name).lower())
        mapping = attrs.pop('mapping', Mapping(doc_type))
        for name, value in list(iteritems(attrs)):
            if isinstance(value, FieldBase):
                mapping.field(name, value)
                del attrs[name]

        # document inheritance
        for b in bases:
            if hasattr(b, '_mapping_'):
                mapping.update(b._mapping_, update_only=True)

        attrs['_mapping_'] = mapping
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)

@add_metaclass(DocTypeMeta)
class DocType(ObjectBase):
    pass
