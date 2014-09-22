from .utils import DslBase
from .field import InnerObject

class Properties(InnerObject, DslBase):
    def __init__(self, name):
        self._name = name
        super(Properties, self).__init__()

    @property
    def name(self):
        return self._name


class Mapping(object):
    def __init__(self, name):
        self.properties = Properties(name)

    def __contains__(self, name):
        return name in self.properties.properties

    def __getitem__(self, name):
        return self.properties.properties[name]

    def __iter__(self):
        return iter(self.properties.properties)

    @property
    def doc_type(self):
        return self.properties.name

    def field(self, *args, **kwargs):
        self.properties.property(*args, **kwargs)
        return self

    def to_dict(self):
        return self.properties.to_dict()
