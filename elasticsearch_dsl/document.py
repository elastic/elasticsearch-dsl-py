from six import iteritems, add_metaclass

from .field import FieldBase
from .mapping import Mapping

class DocTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        mapping = attrs.pop('mapping', Mapping(name))
        for name, value in list(iteritems(attrs)):
            if isinstance(value, FieldBase):
                mapping.field(name, value)
                del attrs[name]
        attrs['_mapping_'] = mapping
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)

@add_metaclass(DocTypeMeta)
class DocType(object):
    pass
