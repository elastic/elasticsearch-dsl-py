from six import iteritems

class DslBase(object):
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

        # TODO: return something that will provide attribute access for inner dicts
        try:
            return self._params[name]
        except KeyError:
            if name in self._param_defs:
                pinfo = self._param_defs[name]
                if pinfo.get('multi'):
                    return self._params.setdefault(name, [])
                elif pinfo.get('hash'):
                    return self._params.setdefault(name, {})
            raise AttributeError()

    def to_dict(self):
        d = {}
        out = {self.name: d}
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
        return out


class DslMeta(type):
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

