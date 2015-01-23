from datetime import date
from dateutil import parser

from .utils import DslBase, _make_dsl_class, ObjectBase, AttrDict

__all__ = ['construct_field', 'Object', 'Nested', 'Date', 'String', 'Float',
    'Double', 'Byte', 'Short', 'Integer', 'Long', 'Boolean', 'Ip', 'Attachment',
    'GeoPoint', 'GeoShape', ]

def construct_field(name_or_field, **params):
    # {"type": "string", "index": "not_analyzed"}
    if isinstance(name_or_field, dict):
        if params:
            raise ValueError('construct_field() cannot accept parameters when passing in a dict.')
        params = name_or_field.copy()
        if 'type' not in params:
            # inner object can be implicitly defined
            if 'properties' in params:
                name = 'object'
            else:
                raise ValueError('construct_field() needs to have a "type" key.')
        else:
            name = params.pop('type')
        return Field.get_dsl_class(name)(**params)

    # String()
    if isinstance(name_or_field, Field):
        if params:
            raise ValueError('construct_field() cannot accept parameters when passing in a construct_field object.')
        return name_or_field

    # "string", index="not_analyzed"
    return Field.get_dsl_class(name_or_field)(**params)

class Field(DslBase):
    _type_name = 'field'
    _type_shortcut = staticmethod(construct_field)
    # all fields can be multifields
    _param_defs = {'fields': {'type': 'field', 'hash': True}}
    name = None

    def _to_python(self, data):
        return data
    
    def to_python(self, data):
        if isinstance(data, list):
            data[:] = map(self._to_python, data)
            return data
        return self._to_python(data)

    def to_dict(self):
        d = super(Field, self).to_dict()
        name, value = d.popitem()
        value['type'] = name
        return value

class InnerObjectWrapper(ObjectBase):
    def __init__(self, mapping, **kwargs):
        # mimic DocType behavior with _doc_type.mapping
        super(AttrDict, self).__setattr__('_doc_type', type('Meta', (), {'mapping': mapping}))
        super(InnerObjectWrapper, self).__init__(**kwargs)


class InnerObject(object):
    " Common functionality for nested and object fields. "
    _doc_class = InnerObjectWrapper
    _param_defs = {'properties': {'type': 'field', 'hash': True}}

    def property(self, name, *args, **kwargs):
        self.properties[name] = construct_field(*args, **kwargs)
        return self

    def empty(self):
        return {}

    def update(self, other_object):
        if not hasattr(other_object, 'properties'):
            # not an inner/nested object, no merge possible
            return

        our, other = self.properties, other_object.properties
        for name in other:
            if name in our:
                if hasattr(our[name], 'update'):
                    our[name].update(other[name])
                continue
            our[name] = other[name]

    def _to_python(self, data):
        # don't wrap already wrapped data
        if isinstance(data, self._doc_class):
            return data

        if isinstance(data, list):
            data[:] = list(map(self._to_python, data))
            return data

        return self._doc_class(self.properties, **data)

class Object(InnerObject, Field):
    name = 'object'

class Nested(InnerObject, Field):
    name = 'nested'

    def empty(self):
        return []

class Date(Field):
    name = 'date'

    def _to_python(self, data):
        if isinstance(data, date):
            return data

        try:
            # TODO: add format awareness
            return parser.parse(data)
        except (TypeError, ValueError):
            raise #XXX

FIELDS = (
    'string',
    'float',
    'double',
    'byte',
    'short',
    'integer',
    'long',
    'boolean',
    'ip',
    'attachment',
    'geo_point',
    'geo_shape',
)

# generate the query classes dynamicaly
for f in FIELDS:
    fclass = _make_dsl_class(Field, f)
    globals()[fclass.__name__] = fclass
    __all__.append(fclass.__name__)

