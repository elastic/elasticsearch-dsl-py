from .utils import DslBase, _make_dsl_class

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

    def to_dict(self):
        d = super(FieldBase, self).to_dict()
        name, value = d.popitem()
        value['type'] = name
        return value

class InnerObject(object):
    " Common functionality for nested and object fields. "
    _param_defs = {'properties': {'type': 'field', 'hash': True}}

    def property(self, name, *args, **kwargs):
        self.properties[name] = Field(*args, **kwargs)
        return self

class Object(InnerObject, FieldBase):
    name = 'object'

class Nested(InnerObject, FieldBase):
    name = 'nested'

FIELDS = (
    'string',
    'date'
)

# generate the query classes dynamicaly
for f in FIELDS:
    fclass = _make_dsl_class(FieldBase, f)
    globals()[fclass.__name__] = fclass


