from datetime import date
from dateutil import parser
from six import itervalues

from .utils import DslBase, _make_dsl_class, ObjectBase, AttrDict, AttrList
from .exceptions import ValidationException

__all__ = [
    'construct_field', 'Field', 'Object', 'Nested', 'Date', 'String', 'Float', 'Double',
    'Byte', 'Short', 'Integer', 'Long', 'Boolean', 'Ip', 'Attachment',
    'GeoPoint', 'GeoShape', 'InnerObjectWrapper'
]

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
    _coerce = False

    def __init__(self, *args, **kwargs):
        self._multi = kwargs.pop('multi', False)
        self._required = kwargs.pop('required', False)
        super(Field, self).__init__(*args, **kwargs)

    def _to_python(self, data):
        return data

    def _empty(self):
        return None

    def empty(self):
        if self._multi:
            return AttrList([])
        return self._empty()

    def to_python(self, data):
        if isinstance(data, (list, AttrList)):
            data[:] = map(self._to_python, data)
            return data
        return self._to_python(data)

    def clean(self, data):
        if data is not None:
            data = self.to_python(data)
        # FIXME: numeric 0
        if not data and self._required:
            raise ValidationException("Value required for this field.")
        return data

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
    _param_defs = {'properties': {'type': 'field', 'hash': True}}
    _coerce = True

    def __init__(self, *args, **kwargs):
        self._doc_class = kwargs.pop('doc_class', InnerObjectWrapper)
        super(InnerObject, self).__init__(*args, **kwargs)

    def field(self, name, *args, **kwargs):
        self.properties[name] = construct_field(*args, **kwargs)
        return self
    # XXX: backwards compatible, will be removed
    property = field

    def _empty(self):
        return self._doc_class(self.properties)

    def empty(self):
        if self._multi:
            return AttrList([], lambda d: self._doc_class(self.properties, **d))
        return self._empty()

    def __getitem__(self, name):
        return self.properties[name]

    def __contains__(self, name):
        return name in self.properties

    def _collect_fields(self):
        " Iterate over all Field objects within, including multi fields. "
        for f in itervalues(self.properties.to_dict()):
            yield f
            # multi fields
            if hasattr(f, 'fields'):
                for inner_f in itervalues(f.fields.to_dict()):
                    yield inner_f
            # nested and inner objects
            if hasattr(f, '_collect_fields'):
                for inner_f in f._collect_fields():
                    yield inner_f

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
        if data is None:
            return None
        # don't wrap already wrapped data
        if isinstance(data, self._doc_class):
            return data

        if isinstance(data, (list, AttrList)):
            data[:] = list(map(self._to_python, data))
            return data

        if isinstance(data, AttrDict):
            data = data._d_

        return self._doc_class(self.properties, **data)

    def clean(self, data):
        data = super(InnerObject, self).clean(data)
        if data is None:
            return None
        if isinstance(data, (list, AttrList)):
            for d in data:
                d.full_clean()
        else:
            data.full_clean()
        return data


class Object(InnerObject, Field):
    name = 'object'

class Nested(InnerObject, Field):
    name = 'nested'

    def __init__(self, *args, **kwargs):
        # change the default for Nested fields
        kwargs.setdefault('multi', True)
        super(Nested, self).__init__(*args, **kwargs)

class Date(Field):
    name = 'date'
    _coerce = True

    def _to_python(self, data):
        if not data:
            return None
        if isinstance(data, date):
            return data

        try:
            # TODO: add format awareness
            return parser.parse(data)
        except Exception as e:
            raise ValidationException('Could not parse date from the value (%r)' % data, e)

class String(Field):
    _param_defs = {
        'fields': {'type': 'field', 'hash': True},
        'analyzer': {'type': 'analyzer'},
        'index_analyzer': {'type': 'analyzer'},
        'search_analyzer': {'type': 'analyzer'},
    }
    name = 'string'

    def _empty(self):
        return ''

FIELDS = (
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
    'completion',
)

# generate the query classes dynamicaly
for f in FIELDS:
    fclass = _make_dsl_class(Field, f)
    globals()[fclass.__name__] = fclass
    __all__.append(fclass.__name__)

