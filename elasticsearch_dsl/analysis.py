from .utils import DslBase, _make_dsl_class

__all__ = [
    'CjkWidthTokenFilter', 'HindiAnalyzer', 'LowercaseTokenFilter',
    'ShingleTokenFilter', 'Tokenizer', 'ClassicTokenFilter',
    'HindiNormalizationTokenFilter', 'LowercaseTokenizer', 'SimpleAnalyzer',
    'TrimTokenFilter', 'Analyzer', 'ClassicTokenizer', 'HtmlStripCharFilter',
    'MappingCharFilter', 'SnowballAnalyzer', 'TruncateTokenFilter',
    'ApostropheTokenFilter', 'CommonGramsTokenFilter', 'HungarianAnalyzer',
    'NGramTokenFilter', 'SnowballTokenFilter', 'TurkishAnalyzer',
    'ArabicAnalyzer', 'CustomAnalyzer', 'HunspellTokenFilter',
    'NGramTokenizer', 'SoraniAnalyzer', 'UaxUrlEmailTokenizer',
    'ArabicNormalizationTokenFilter', 'CzechAnalyzer',
    'HyphenationDecompounderTokenFilter', 'NorwegianAnalyzer',
    'SoraniNormalizationTokenFilter', 'UniqueTokenFilter', 'ArmenianAnalyzer',
    'DanishAnalyzer', 'IndicNormalizationTokenFilter',
    'PathHierarchyTokenizer', 'SpanishAnalyzer', 'UppercaseTokenFilter',
    'AsciifoldingTokenFilter', 'DelimitedPayloadFilterTokenFilter',
    'IndonesianAnalyzer', 'PatternAnalyzer', 'StandardAnalyzer',
    'WhitespaceAnalyzer', 'BasqueAnalyzer',
    'DictionaryDecompounderTokenFilter', 'IrishAnalyzer',
    'PatternCaptureTokenFilter', 'StandardTokenFilter', 'WhitespaceTokenizer',
    'BrazilianAnalyzer', 'ItalianAnalyzer', 'PatternReplaceCharFilter',
    'StandardTokenizer', 'WordDelimiterTokenFilter', 'BuiltinAnalyzer',
    'DutchAnalyzer', 'KeepTokenFilter', 'PatternReplaceTokenFilter',
    'StemmerOverrideTokenFilter', 'BuiltinCharFilter', 'EdgeNGramTokenFilter',
    'KeepTypesTokenFilter', 'PatternTokenizer', 'StemmerTokenFilter',
    'BuiltinTokenFilter', 'EdgeNGramTokenizer', 'KeywordAnalyzer',
    'PersianAnalyzer', 'StopAnalyzer', 'analyzer', 'BuiltinTokenizer',
    'ElisionTokenFilter', 'KeywordMarkerTokenFilter',
    'PersianNormalizationTokenFilter', 'StopTokenFilter', 'BulgarianAnalyzer',
    'EnglishAnalyzer', 'KeywordRepeatTokenFilter', 'PorterStemTokenFilter',
    'SwedishAnalyzer', 'char_filter', 'FinnishAnalyzer', 'KeywordTokenizer',
    'PortugueseAnalyzer', 'SynonymTokenFilter', 'CatalanAnalyzer',
    'FrenchAnalyzer', 'KstemTokenFilter', 'ReverseTokenFilter', 'token_filter',
    'CharFilter', 'GalicianAnalyzer', 'LatvianAnalyzer', 'RomanianAnalyzer',
    'tokenizer', 'ChineseAnalyzer', 'GermanAnalyzer', 'LengthTokenFilter',
    'RussianAnalyzer', 'ThaiAnalyzer', 'CjkAnalyzer',
    'GermanNormalizationTokenFilter', 'LetterTokenizer', 'ScandinavianFolding',
    'TokenFilter', 'ThaiTokenizer', 'CjkBigramTokenFilter', 'GreekAnalyzer',
    'LimitTokenFilter', 'ScandinavianNormalizationTokenFilter', 'TokenFilter'
]

ANALYZERS = frozenset((
    'standard', 'simple', 'whitespace', 'stop', 'keyword', 'pattern', 'snowball',

    # lang analyzers:
    'arabic', 'armenian', 'basque', 'brazilian', 'bulgarian', 'catalan', 'chinese',
    'cjk', 'czech', 'danish', 'dutch', 'english', 'finnish', 'french', 'galician',
    'german', 'greek', 'hindi', 'hungarian', 'indonesian', 'irish', 'italian',
    'latvian', 'norwegian', 'persian', 'portuguese', 'romanian', 'russian',
    'sorani', 'spanish', 'swedish', 'turkish', 'thai',
))

TOKENIZERS = frozenset((    
    'standard', 'edgeNGram', 'keyword', 'letter', 'lowercase', 'nGram',
    'whitespace', 'pattern', 'uax_url_email', 'path_hierarchy', 'classic',
    'thai',
))

TOKEN_FILTERS = frozenset((
    'standard', 'asciifolding', 'length', 'lowercase', 'uppercase', 'nGram',
    'edgeNGram', 'porter_stem', 'shingle', 'stop', 'word_delimiter', 'stemmer',
    'stemmer_override', 'keyword_marker', 'keyword_repeat', 'kstem',
    'snowball', 'synonym', 'dictionary_decompounder',
    'hyphenation_decompounder', 'reverse', 'elision', 'truncate', 'unique',
    'pattern_capture', 'pattern_replace', 'trim', 'limit', 'hunspell',
    'common_grams', 'cjk_width', 'cjk_bigram', 'delimited_payload_filter',
    'keep', 'keep_types', 'classic', 'apostrophe',

    # language normalizations
    'arabic_normalization', 'german_normalization', 'hindi_normalization',
    'indic_normalization', 'sorani_normalization', 'persian_normalization',
    'scandinavian_normalization', 'scandinavian_folding ',
))


CHAR_FILTERS = frozenset((
    'html_strip', 'mapping', 'pattern_replace',
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
        
        if name_or_instance in cls._builtins and not type:
            if kwargs:
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

    def get_analysis_definition(self):
        d = self.definition()
        # empty definition, assume external
        if len(d) == 1 and 'type' in d:
            return {}
        return {'analyzer': {self._name: d}}

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
        out = super(CustomAnalyzer, self).get_analysis_definition()
        # empty definition, assume external
        if not out:
            return out

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

class NGramTokenizer(Tokenizer):
    name = 'nGram'

class EdgeNGramTokenizer(Tokenizer):
    name = 'edgeNGram'

class TokenFilter(AnalysisBase, DslBase):
    _type_name = 'token_filter'
    _builtins = TOKEN_FILTERS
    name = None

class BuiltinTokenFilter(TokenFilter):
    name = 'builtin'

class NGramTokenFilter(TokenFilter):
    name = 'nGram'

class EdgeNGramTokenFilter(TokenFilter):
    name = 'edgeNGram'


class CharFilter(AnalysisBase, DslBase):
    _type_name = 'char_filter'
    _builtins = CHAR_FILTERS
    name = None

class BuiltinCharFilter(CharFilter):
    name = 'builtin'


# shortcuts for direct use
analyzer = Analyzer._type_shortcut
tokenizer = Tokenizer._type_shortcut
token_filter = TokenFilter._type_shortcut
char_filter = CharFilter._type_shortcut


# dynamically create all analysis classes:
for base in (Tokenizer, TokenFilter, CharFilter, Analyzer):
    for name in base._builtins:
        # skip manually defined classes
        if name in base._classes:
            continue

        analysis_class = _make_dsl_class(base, name, suffix=base.__name__)
        globals()[analysis_class.__name__] = analysis_class
