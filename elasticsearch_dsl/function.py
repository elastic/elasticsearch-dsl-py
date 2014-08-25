from six import add_metaclass

from .utils import DslMeta, DslBase

class ScoreFunctionMeta(DslMeta):
    _classes = {}

def SF(name_or_sf, **params):
    # {"script_score": {"script": "_score"}, "filter": {}}
    if isinstance(name_or_sf, dict):
        if params:
            raise #XXX
        kwargs = {}
        sf = name_or_sf.copy()
        for k in ScoreFunction._param_defs:
            if k in name_or_sf:
                kwargs[k] = sf.pop(k)
        if len(sf) != 1:
            raise #XXX
        name, params = sf.popitem()
        # boost factor special case, see elasticsearch #6343
        if not isinstance(params, dict):
            params = {'value': params}
        kwargs.update(params)
        return ScoreFunction.get_dsl_class(name)(**kwargs)

    # ScriptScore(script="_score", filter=F())
    if isinstance(name_or_sf, ScoreFunction):
        if params:
            raise #XXX
        return name_or_sf

    # "script_score", script="_score", filter=F()
    return ScoreFunction.get_dsl_class(name_or_sf)(**params)

@add_metaclass(ScoreFunctionMeta)
class ScoreFunction(DslBase):
    _type_name = 'score_function'
    _type_shortcut = staticmethod(SF)
    _param_defs = {
        'query': {'type': 'query'},
        'filter': {'type': 'filter'},
    }
    name = None

    def to_dict(self):
        d = super(ScoreFunction, self).to_dict()
        # filter and query dicts should be at the same level as us
        for k in self._param_defs:
            if k in d[self.name]:
                d[k] = d[self.name].pop(k)
        return d

class ScriptScore(ScoreFunction):
    name = 'script_score'

class BoostFactor(ScoreFunction):
    name = 'boost_factor'

    def to_dict(self):
        d = super(BoostFactor, self).to_dict()
        if 'value' in d[self.name]:
            d[self.name] = d[self.name].pop('value')
        return d

class Random(ScoreFunction):
    name = 'random'

class FieldValueFactor(ScoreFunction):
    name = 'field_value_factor'

class Linear(ScoreFunction):
    name = 'linear'
    
class Gauss(ScoreFunction):
    name = 'gauss'
    
class Exp(ScoreFunction):
    name = 'exp'
    
