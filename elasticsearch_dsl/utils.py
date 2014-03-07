class DslMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(DslMeta, cls).__new__(cls, name, bases, attrs)
        cls._classes[new_class.name] = new_class
        return new_class

    @classmethod
    def get_dsl_obj(cls, name, params):
        try:
            DslClass = cls._classes[name]
        except KeyError:
            raise #XXX
        return DslClass(**params)

    @classmethod
    def from_dict(cls, query):
        if len(query) != 1:
            raise #XXX
        name, params = query.popitem()
        return cls.get_dsl_obj(name, params)
