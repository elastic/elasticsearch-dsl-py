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

    def field(self, *args, **kwargs):
        self.properties.property(*args, **kwargs)
        return self

    def to_dict(self):
        return self.properties.to_dict()
