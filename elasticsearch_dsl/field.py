from .utils import DslBase, _make_dsl_class, ObjectBase, AttrDict

# Field because F is for Filter
def Field(name_or_field, **params):
    # {"type": "string", "index": "not_analyzed"}
    if isinstance(name_or_field, dict):
        if params:
            raise ValueError('Field() cannot accept parameters when passing in a dict.')
        if 'type' not in name_or_field:
            raise ValueError('Field() needs to have a "type" key.')
        params = name_or_field.copy()
        name = params.pop('type')
        return FieldBase.get_dsl_class(name)(**params)

    # String()
    if isinstance(name_or_field, FieldBase):
        if params:
            raise ValueError('Field() cannot accept parameters when passing in a Field object.')
        return name_or_field

    # "string", index="not_analyzed"
    return FieldBase.get_dsl_class(name_or_field)(**params)

class FieldBase(DslBase):
    _type_name = 'field'
    _type_shortcut = staticmethod(Field)
    # all fields can be multifields
    _param_defs = {'fields': {'type': 'field', 'hash': True}}
    name = None

    def to_python(self, data):
        return data

    def to_dict(self):
        d = super(FieldBase, self).to_dict()
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
        self.properties[name] = Field(*args, **kwargs)
        return self

    def empty(self):
        return self.to_python({})

    def to_python(self, data):
        # don't wrap already wrapped data
        if isinstance(data, self._doc_class):
            return data

        return self._doc_class(self.properties, **data)

class Object(InnerObject, FieldBase):
    name = 'object'

class Nested(InnerObject, FieldBase):
    name = 'nested'

# TODO: add to_python
FIELDS = (
    'string',
    'date'
)

# generate the query classes dynamicaly
for f in FIELDS:
    fclass = _make_dsl_class(FieldBase, f)
    globals()[fclass.__name__] = fclass


