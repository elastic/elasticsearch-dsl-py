from typing import TYPE_CHECKING, Any, List, Literal, Mapping, TypedDict, Union
from elasticsearch_dsl.search_base import InstrumentedField
from elasticsearch_dsl.utils import AttrDict

if TYPE_CHECKING:
    from elasticsearch_dsl import analysis, function, wrappers

PipeSeparatedFlags = str


class QueryBase(TypedDict):
    boost: float
    _name: str


class FuzzyQuery(QueryBase):
    max_expansions: int
    prefix_length: int
    rewrite: str
    transpositions: bool
    fuzziness: Union[str, int]
    value: Union[str, float, bool]


class SpanTermQuery(QueryBase):
    value: str


class CommonTermsQuery(QueryBase):
    analyzer: str
    cutoff_frequency: float
    high_freq_operator: Literal["and", "or"]
    low_freq_operator: Literal["and", "or"]
    minimum_should_match: Union[int, str]
    query: str


class RankFeatureFunction(TypedDict):
    pass


class RankFeatureFunctionSaturation(RankFeatureFunction):
    pivot: float


class MatchPhraseQuery(QueryBase):
    analyzer: str
    query: str
    slop: int
    zero_terms_query: Literal["all", "none"]


class FunctionScoreContainer(TypedDict):
    exp: Union["function.UntypedDecayFunction", "function.DateDecayFunction", "function.NumericDecayFunction", "function.GeoDecayFunction"]
    gauss: Union["function.UntypedDecayFunction", "function.DateDecayFunction", "function.NumericDecayFunction", "function.GeoDecayFunction"]
    linear: Union["function.UntypedDecayFunction", "function.DateDecayFunction", "function.NumericDecayFunction", "function.GeoDecayFunction"]
    field_value_factor: "function.FieldValueFactorScoreFunction"
    random_score: "function.RandomScoreFunction"
    script_score: "function.ScriptScoreFunction"
    filter: Query
    weight: float


class InnerHits(TypedDict):
    name: str
    size: int
    from: int
    collapse: "i.FieldCollapse"
    docvalue_fields: List["i.FieldAndFormat"]
    explain: bool
    highlight: "i.Highlight"
    ignore_unmapped: bool
    script_fields: Mapping[Union[str, "InstrumentedField"], "i.ScriptField"]
    seq_no_primary_term: bool
    fields: Union[Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]]]
    sort: Union[Union[Union[str, "InstrumentedField"], "i.SortOptions"], List[Union[Union[str, "InstrumentedField"], "i.SortOptions"]]]
    _source: Union[bool, "i.SourceFilter"]
    stored_fields: Union[Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]]]
    track_scores: bool
    version: bool


class WildcardQuery(QueryBase):
    case_insensitive: bool
    rewrite: str
    value: str
    wildcard: str


class RegexpQuery(QueryBase):
    case_insensitive: bool
    flags: str
    max_determinized_states: int
    rewrite: str
    value: str


class LikeDocument(TypedDict):
    doc: Any
    fields: List[Union[str, "InstrumentedField"]]
    _id: str
    _index: str
    per_field_analyzer: Mapping[Union[str, "InstrumentedField"], str]
    routing: str
    version: int
    version_type: Literal["internal", "external", "external_gte", "force"]


class TermsSetQuery(QueryBase):
    minimum_should_match_field: Union[str, "InstrumentedField"]
    minimum_should_match_script: "i.Script"
    terms: List[str]


class SpanQuery(TypedDict):
    span_containing: "i.SpanContainingQuery"
    span_field_masking: "i.SpanFieldMaskingQuery"
    span_first: "i.SpanFirstQuery"
    span_gap: Mapping[Union[str, "InstrumentedField"], int]
    span_multi: "i.SpanMultiTermQuery"
    span_near: "i.SpanNearQuery"
    span_not: "i.SpanNotQuery"
    span_or: "i.SpanOrQuery"
    span_term: Mapping[Union[str, "InstrumentedField"], "i.SpanTermQuery"]
    span_within: "i.SpanWithinQuery"


class PrefixQuery(QueryBase):
    rewrite: str
    value: str
    case_insensitive: bool


class TokenPruningConfig(TypedDict):
    tokens_freq_ratio_threshold: int
    tokens_weight_threshold: float
    only_score_pruned_tokens: bool


class RankFeatureFunctionLinear(RankFeatureFunction):
    pass


class TextExpansionQuery(QueryBase):
    model_id: str
    model_text: str
    pruning_config: "i.TokenPruningConfig"


class MatchBoolPrefixQuery(QueryBase):
    analyzer: str
    fuzziness: Union[str, int]
    fuzzy_rewrite: str
    fuzzy_transpositions: bool
    max_expansions: int
    minimum_should_match: Union[int, str]
    operator: Literal["and", "or"]
    prefix_length: int
    query: str


class Script(TypedDict):
    source: str
    id: str
    params: Mapping[str, Any]
    lang: Literal["painless", "expression", "mustache", "java"]
    options: Mapping[str, str]


class PinnedDoc(TypedDict):
    _id: str
    _index: str


class QueryVectorBuilder(TypedDict):
    text_embedding: "i.TextEmbedding"


class RankFeatureFunctionSigmoid(RankFeatureFunction):
    pivot: float
    exponent: float


class IntervalsQuery(QueryBase):
    all_of: "i.IntervalsAllOf"
    any_of: "i.IntervalsAnyOf"
    fuzzy: "i.IntervalsFuzzy"
    match: "i.IntervalsMatch"
    prefix: "i.IntervalsPrefix"
    wildcard: "i.IntervalsWildcard"


class RankFeatureFunctionLogarithm(RankFeatureFunction):
    scaling_factor: float


class TermQuery(QueryBase):
    value: Union[int, float, str, bool, None, Any]
    case_insensitive: bool


class MatchQuery(QueryBase):
    analyzer: str
    auto_generate_synonyms_phrase_query: bool
    cutoff_frequency: float
    fuzziness: Union[str, int]
    fuzzy_rewrite: str
    fuzzy_transpositions: bool
    lenient: bool
    max_expansions: int
    minimum_should_match: Union[int, str]
    operator: Literal["and", "or"]
    prefix_length: int
    query: Union[str, float, bool]
    zero_terms_query: Literal["all", "none"]


class WeightedTokensQuery(QueryBase):
    tokens: Mapping[str, float]
    pruning_config: "i.TokenPruningConfig"


class MatchPhrasePrefixQuery(QueryBase):
    analyzer: str
    max_expansions: int
    query: str
    slop: int
    zero_terms_query: Literal["all", "none"]


class ScriptField(TypedDict):
    script: "i.Script"
    ignore_failure: bool


class SourceFilter(TypedDict):
    excludes: Union[Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]]]
    includes: Union[Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]]]


class FieldAndFormat(TypedDict):
    field: Union[str, "InstrumentedField"]
    format: str
    include_unmapped: bool


class HighlightBase(TypedDict):
    type: Literal["plain", "fvh", "unified"]
    boundary_chars: str
    boundary_max_scan: int
    boundary_scanner: Literal["chars", "sentence", "word"]
    boundary_scanner_locale: str
    force_source: bool
    fragmenter: Literal["simple", "span"]
    fragment_size: int
    highlight_filter: bool
    highlight_query: Query
    max_fragment_length: int
    max_analyzed_offset: int
    no_match_size: int
    number_of_fragments: int
    options: Mapping[str, Any]
    order: Literal["score"]
    phrase_limit: int
    post_tags: List[str]
    pre_tags: List[str]
    require_field_match: bool
    tags_schema: Literal["styled"]


class Highlight(HighlightBase):
    encoder: Literal["default", "html"]
    fields: Mapping[Union[str, "InstrumentedField"], "i.HighlightField"]


class FieldCollapse(TypedDict):
    field: Union[str, "InstrumentedField"]
    inner_hits: Union["i.InnerHits", List["i.InnerHits"]]
    max_concurrent_group_searches: int
    collapse: "i.FieldCollapse"


class SortOptions(TypedDict):
    _score: "i.ScoreSort"
    _doc: "i.ScoreSort"
    _geo_distance: "i.GeoDistanceSort"
    _script: "i.ScriptSort"


class SpanMultiTermQuery(QueryBase):
    match: Query


class SpanNotQuery(QueryBase):
    dist: int
    exclude: "i.SpanQuery"
    include: "i.SpanQuery"
    post: int
    pre: int


class SpanWithinQuery(QueryBase):
    big: "i.SpanQuery"
    little: "i.SpanQuery"


class SpanFirstQuery(QueryBase):
    end: int
    match: "i.SpanQuery"


class SpanOrQuery(QueryBase):
    clauses: List["i.SpanQuery"]


class SpanNearQuery(QueryBase):
    clauses: List["i.SpanQuery"]
    in_order: bool
    slop: int


class SpanFieldMaskingQuery(QueryBase):
    field: Union[str, "InstrumentedField"]
    query: "i.SpanQuery"


class SpanContainingQuery(QueryBase):
    big: "i.SpanQuery"
    little: "i.SpanQuery"


class TextEmbedding(TypedDict):
    model_id: str
    model_text: str


class IntervalsWildcard(TypedDict):
    analyzer: str
    pattern: str
    use_field: Union[str, "InstrumentedField"]


class IntervalsAnyOf(TypedDict):
    intervals: List["i.IntervalsContainer"]
    filter: "i.IntervalsFilter"


class IntervalsFuzzy(TypedDict):
    analyzer: str
    fuzziness: Union[str, int]
    prefix_length: int
    term: str
    transpositions: bool
    use_field: Union[str, "InstrumentedField"]


class IntervalsPrefix(TypedDict):
    analyzer: str
    prefix: str
    use_field: Union[str, "InstrumentedField"]


class IntervalsMatch(TypedDict):
    analyzer: str
    max_gaps: int
    ordered: bool
    query: str
    use_field: Union[str, "InstrumentedField"]
    filter: "i.IntervalsFilter"


class IntervalsAllOf(TypedDict):
    intervals: List["i.IntervalsContainer"]
    max_gaps: int
    ordered: bool
    filter: "i.IntervalsFilter"


class HighlightField(HighlightBase):
    fragment_offset: int
    matched_fields: Union[Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]]]
    analyzer: Union["analysis.CustomAnalyzer", "analysis.FingerprintAnalyzer", "analysis.KeywordAnalyzer", "analysis.LanguageAnalyzer", "analysis.NoriAnalyzer", "analysis.PatternAnalyzer", "analysis.SimpleAnalyzer", "analysis.StandardAnalyzer", "analysis.StopAnalyzer", "analysis.WhitespaceAnalyzer", "analysis.IcuAnalyzer", "analysis.KuromojiAnalyzer", "analysis.SnowballAnalyzer", "analysis.DutchAnalyzer"]


class GeoDistanceSort(TypedDict):
    mode: Literal["min", "max", "sum", "avg", "median"]
    distance_type: Literal["arc", "plane"]
    ignore_unmapped: bool
    order: Literal["asc", "desc"]
    unit: Literal["in", "ft", "yd", "mi", "nmi", "km", "m", "cm", "mm"]
    nested: "i.NestedSortValue"


class ScriptSort(TypedDict):
    order: Literal["asc", "desc"]
    script: "i.Script"
    type: Literal["string", "number", "version"]
    mode: Literal["min", "max", "sum", "avg", "median"]
    nested: "i.NestedSortValue"


class ScoreSort(TypedDict):
    order: Literal["asc", "desc"]


class IntervalsFilter(TypedDict):
    after: "i.IntervalsContainer"
    before: "i.IntervalsContainer"
    contained_by: "i.IntervalsContainer"
    containing: "i.IntervalsContainer"
    not_contained_by: "i.IntervalsContainer"
    not_containing: "i.IntervalsContainer"
    not_overlapping: "i.IntervalsContainer"
    overlapping: "i.IntervalsContainer"
    script: "i.Script"


class IntervalsContainer(TypedDict):
    all_of: "i.IntervalsAllOf"
    any_of: "i.IntervalsAnyOf"
    fuzzy: "i.IntervalsFuzzy"
    match: "i.IntervalsMatch"
    prefix: "i.IntervalsPrefix"
    wildcard: "i.IntervalsWildcard"


class NestedSortValue(TypedDict):
    filter: Query
    max_children: int
    nested: "i.NestedSortValue"
    path: Union[str, "InstrumentedField"]


