class DslMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(DslMeta, cls).__new__(cls, name, bases, attrs)
        cls._classes[new_class.name] = new_class
        return new_class

    @classmethod
    def get_dsl_class(cls, name):
        try:
            return cls._classes[name]
        except KeyError:
            raise #XXX
