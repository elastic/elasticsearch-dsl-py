from six import iteritems

class AttrDict(object):
    """
    Helper class to provide attribute like access (read and write) to
    dictionaries. Used to provide a convenient way to access both results and
    nested dsl dicts.
    """
    def __init__(self, d):
        # assign the inner dict manually to prevent __setattr__ from firing
        super(AttrDict, self).__setattr__('_d', d)

    def __dir__(self):
        # introspection for auto-complete in IPython etc
        return list(self._d.keys())

    def __eq__(self, other):
        if isinstance(other, AttrDict):
            return other._d == self._d
        # make sure we still equal to a dict with the same data
        return other == self._d

    def __repr__(self):
        r = repr(self._d)
        if len(r) > 60:
            r = r[:60] + '...}'
        return r

    def __getattr__(self, attr_name):
        try:
            d = self._d[attr_name]
            # wrap nested dicts in AttrDict as well to preserve attr access
            if isinstance(d, dict):
                return AttrDict(d)
            return d
        except KeyError:
            raise AttributeError()

    def __getitem__(self, key):
        # don't wrap things whe accessing via __getitem__ for consistency
        return self._d[key]

    def __setitem__(self, key, value):
        self._d[key] = value
    __setattr__ = __setitem__


class DslBase(object):
    """
    Base class for all DSL objects - queries, filters, aggregations etc. Wraps
    a dictionary representing the object's json.

    Provides several feature:
        - attribute access to the wrapped dictionary (.field instead of ['field'])
        - _clone method returning a deep copy of self
        - to_dict method to serialize into dict (to be sent via elasticsearch-py)
        - basic logical operators (&, | and ~) using a Bool(Filter|Query) TODO:
          move into a class specific for Query/Filter
        - respects the definiton of the class and (de)serializes it's
          attributes based on the `_param_defs` definition (for example turning
          all values in the `must` attribute into Query objects)
    """
    _param_defs = {}

    def __init__(self, **params):
        self._params = {}
        for pname, pvalue in iteritems(params):
            setattr(self, pname, pvalue)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.to_dict() == self.to_dict()

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super(DslBase, self).__setattr__(name, value)

        if name in self._param_defs:
            pinfo = self._param_defs[name]

            if 'type' in pinfo:
                shortcut = self.__class__.get_dsl_type(pinfo['type'])
                if pinfo.get('multi'):
                    value = list(map(shortcut, value))
                elif pinfo.get('hash'):
                    d = {}
                    for k, v in iteritems(value):
                        v = shortcut({k: v})
                        d[v._name] = v
                    value = d
                else:
                    value = shortcut(value)
        self._params[name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError()

        value = None
        try:
            value = self._params[name]
        except KeyError:
            if name in self._param_defs:
                pinfo = self._param_defs[name]
                if pinfo.get('multi'):
                    value = self._params.setdefault(name, [])
                elif pinfo.get('hash'):
                    value = self._params.setdefault(name, {})
        if value is None:
            raise AttributeError()

        if isinstance(value, dict):
            return AttrDict(value)
        return value

    def to_dict(self):
        d = {}
        for pname, value in iteritems(self._params):
            pinfo = self._param_defs.get(pname)
            if pinfo and 'type' in pinfo:
                # don't serialize empty lists and dicts for typed fields
                if not value:
                    continue
                if pinfo.get('multi'):
                    value = list(map(lambda x: x.to_dict(), value))
                elif pinfo.get('hash'):
                    new_value = {}
                    for v in value.values():
                        new_value.update(v.to_dict())
                    value = new_value
                else:
                    value = value.to_dict()
            d[pname] = value
        return {self.name: d}

    def _clone(self):
        return self._type_shortcut(self.to_dict())

    def __add__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__radd__'):
            return other.__radd__(self)
        return self._bool(must=[self, other])

    def __invert__(self):
        return self._bool(must_not=[self])

    def __or__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__ror__'):
            return other.__ror__(self)
        return self._bool(should=[self, other])

    def __and__(self, other):
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, '__rand__'):
            return other.__rand__(self)
        return self._bool(must=[self, other])


class DslMeta(type):
    """
    Base Metaclass for DslBase subclasses that builds a registry of all classes
    for given DslBase subclass (== all the query types for the Query subclass
    of DslBase).

    It then uses the information from that registry (as well as `name` and
    `shortcut` attributes from the base class) to construct any subclass based
    on it's name.

    For typical use see `QueryMeta` and `Query` in `elasticsearch_dsl.query`.
    """
    _types = {}
    def __new__(cls, name, bases, attrs):
        new_class = super(DslMeta, cls).__new__(cls, name, bases, attrs)
        if new_class.name is None:
            # abstract base class, register it's shortcut
            cls._types[new_class._type_name] = new_class._type_shortcut
        else:
            # normal class, register it
            cls._classes[new_class.name] = new_class
        return new_class

    @classmethod
    def get_dsl_type(cls, name):
        try:
            return cls._types[name]
        except KeyError:
            raise #XXX

    @classmethod
    def get_dsl_class(cls, name):
        try:
            return cls._classes[name]
        except KeyError:
            raise #XXX


class BoolMixin(object):
    """
    Mixin containing all the operator overrides for Bool queries and filters.
    """
    def __add__(self, other):
        q = self._clone()
        if isinstance(other, self.__class__):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
        else:
            q.must.append(other)
        return q
    __radd__ = __add__

    def __or__(self, other):
        if not (self.must or self.must_not):
            # TODO: if only 1 in must or should, append the query instead of other
            q = self._clone()
            q.should.append(other)
            return q

        elif isinstance(other, self.__class__) and not (other.must or other.must_not):
            # TODO: if only 1 in must or should, append the query instead of self
            q = other._clone()
            q.should.append(self)
            return q

        return super(self.__class__, self).__or__(other)
    __ror__ = __or__

    def __invert__(self):
        # special case for single negated query
        if not (self.must or self.should) and len(self.must_not) == 1:
            return self.must_not[0]._clone()

        # bol without should, just flip must and must_not
        elif not self.should:
            q = self._clone()
            q.must, q.must_not = q.must_not, q.must
            return q

        # TODO: should -> must_not.append(self.__class__(should=self.should)) ??
        # queries with should just invert normally
        return super(self.__class__, self).__invert__()
