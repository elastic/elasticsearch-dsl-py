from .utils import DslBase

ANALYZERS = frozenset((
    'standard', 'snowball', 'english'
))

TOKENIZERS = frozenset((    
    'keyword', 'standard'
))

TOKEN_FILTERS = frozenset((
    'lowercase', 'standard', 'snowball', 'stop'
))

CHAR_FILTERS = frozenset((
    'html_strip',
))

class AnalysisBase(object):
    def __init__(self, name, **kwargs):
        self._name = name
        super(AnalysisBase, self).__init__(**kwargs)

    def to_dict(self):
        # only name to present in lists
        return self._name

    def definition(self):
        d = super(AnalysisBase, self).to_dict()
        d[self.name]['type'] = self.name
        return d[self.name]

    @classmethod
    def _type_shortcut(cls, name_or_instance, type=None, **kwargs):
        if isinstance(name_or_instance, cls):
            if type or kwargs:
                raise ValueError('%s() cannot accept parameters.' % cls.__name__)
            return name_or_instance
        
        if name_or_instance in cls._builtins:
            if type or kwargs:
                raise ValueError('Builtin %s doesn\'t accept any parameters.' & cls.__name__)
            type = 'builtin'

        # for analyzers
        if type is None:
            type = 'custom'
        return cls.get_dsl_class(type)(name_or_instance, **kwargs)

class Analyzer(AnalysisBase, DslBase):
    _type_name = 'analyzer'
    _builtins = ANALYZERS
    name = None

class BuiltinAnalyzer(Analyzer):
    name = 'builtin'

class CustomAnalyzer(Analyzer):
    name = 'custom'
    _param_defs = {
        'filter': {'type': 'token_filter', 'multi': True},
        'char_filter': {'type': 'char_filter', 'multi': True},
        'tokenizer': {'type': 'tokenizer'},
    }

    def get_analysis_definition(self):
        d = self.definition()
        if d == {'type': 'custom'}:
            return {}
        out = {'analyzer': {self._name: d}}

        t = getattr(self, 'tokenizer', None)
        if t is not None and not isinstance(t, BuiltinTokenizer):
            out['tokenizer'] = {t._name: t.definition()}

        filters = dict((f._name, f.definition())
                for f in self.filter if not isinstance(f, BuiltinTokenFilter))
        if filters:
            out['filter'] = filters

        char_filters = dict((f._name, f.definition())
                for f in self.char_filter if not isinstance(f, BuiltinCharFilter))
        if char_filters:
            out['char_filter'] = char_filters
        return out


class Tokenizer(AnalysisBase, DslBase):
    _type_name = 'tokenizer'
    _builtins = TOKENIZERS
    name = None

class BuiltinTokenizer(Tokenizer):
    name = 'builtin'

class NGram(Tokenizer):
    name = 'ngram'

class Keyword(Tokenizer):
    name = 'keyword'


class TokenFilter(AnalysisBase, DslBase):
    _type_name = 'token_filter'
    _builtins = TOKEN_FILTERS
    name = None

class BuiltinTokenFilter(TokenFilter):
    name = 'builtin'

class Stop(TokenFilter):
    name = 'stop'

class Lower(TokenFilter):
    name = 'lower'


class CharFilter(AnalysisBase, DslBase):
    _type_name = 'char_filter'
    _builtins = CHAR_FILTERS
    name = None

class BuiltinCharFilter(CharFilter):
    name = 'builtin'

class Mapping(CharFilter):
    name = 'mapping'

class PatternReplace(CharFilter):
    name = 'pattern_replace'


# shortcuts for direct use
analyzer = Analyzer._type_shortcut
tokenizer = Tokenizer._type_shortcut
token_filter = TokenFilter._type_shortcut
char_filter = CharFilter._type_shortcut
