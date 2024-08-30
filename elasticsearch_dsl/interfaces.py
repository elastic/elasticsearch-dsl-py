#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

from typing import Any, Dict, List, Literal, Mapping, Union

from elasticsearch_dsl import Query
from elasticsearch_dsl import analysis as a
from elasticsearch_dsl import function as f
from elasticsearch_dsl import interfaces as i
from elasticsearch_dsl.document_base import InstrumentedField
from elasticsearch_dsl.utils import NOT_SET, AttrDict, NotSet

PipeSeparatedFlags = str


class QueryBase(AttrDict[Any]):
    """
    :arg boost: Floating point number used to decrease or increase the
        relevance scores of the query. Boost values are relative to the
        default value of 1.0. A boost value between 0 and 1.0 decreases
        the relevance score. A value greater than 1.0 increases the
        relevance score.
    :arg _name: No documentation available.
    """

    def __init__(
        self,
        *,
        boost: Union[float, "NotSet"] = NOT_SET,
        _name: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if boost != NOT_SET:
            kwargs["boost"] = boost
        if _name != NOT_SET:
            kwargs["_name"] = _name
        super().__init__(kwargs)


class TermQuery(QueryBase):
    """
    :arg value: (required)Term you wish to find in the provided field.
    :arg case_insensitive: Allows ASCII case insensitive matching of the
        value with the indexed field values when set to `true`. When
        `false`, the case sensitivity of matching depends on the
        underlying field’s mapping.
    """

    def __init__(
        self,
        *,
        value: Union[int, float, str, bool, None, Any, "NotSet"] = NOT_SET,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if value != NOT_SET:
            kwargs["value"] = value
        if case_insensitive != NOT_SET:
            kwargs["case_insensitive"] = case_insensitive
        super().__init__(**kwargs)


class TextExpansionQuery(QueryBase):
    """
    :arg model_id: (required)The text expansion NLP model to use
    :arg model_text: (required)The query text
    :arg pruning_config: Token pruning configurations
    """

    def __init__(
        self,
        *,
        model_id: Union[str, "NotSet"] = NOT_SET,
        model_text: Union[str, "NotSet"] = NOT_SET,
        pruning_config: Union[
            "i.TokenPruningConfig", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if model_id != NOT_SET:
            kwargs["model_id"] = model_id
        if model_text != NOT_SET:
            kwargs["model_text"] = model_text
        if pruning_config != NOT_SET:
            kwargs["pruning_config"] = pruning_config
        super().__init__(**kwargs)


class QueryVectorBuilder(AttrDict[Any]):
    """
    :arg text_embedding: No documentation available.
    """

    def __init__(
        self,
        *,
        text_embedding: Union["i.TextEmbedding", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if text_embedding != NOT_SET:
            kwargs["text_embedding"] = text_embedding
        super().__init__(kwargs)


class DistanceFeatureQueryBase(QueryBase):
    """
    :arg origin: (required)Date or point of origin used to calculate
        distances. If the `field` value is a `date` or `date_nanos` field,
        the `origin` value must be a date. Date Math, such as `now-1h`, is
        supported. If the field value is a `geo_point` field, the `origin`
        value must be a geopoint.
    :arg pivot: (required)Distance from the `origin` at which relevance
        scores receive half of the `boost` value. If the `field` value is
        a `date` or `date_nanos` field, the `pivot` value must be a time
        unit, such as `1h` or `10d`. If the `field` value is a `geo_point`
        field, the `pivot` value must be a distance unit, such as `1km` or
        `12m`.
    :arg field: (required)Name of the field used to calculate distances.
        This field must meet the following criteria: be a `date`,
        `date_nanos` or `geo_point` field; have an `index` mapping
        parameter value of `true`, which is the default; have an
        `doc_values` mapping parameter value of `true`, which is the
        default.
    """

    def __init__(
        self,
        *,
        origin: Any = NOT_SET,
        pivot: Any = NOT_SET,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if origin != NOT_SET:
            kwargs["origin"] = origin
        if pivot != NOT_SET:
            kwargs["pivot"] = pivot
        if field != NOT_SET:
            kwargs["field"] = str(field)
        super().__init__(**kwargs)


class UntypedDistanceFeatureQuery(DistanceFeatureQueryBase):
    pass


class InnerHits(AttrDict[Any]):
    """
    :arg name: The name for the particular inner hit definition in the
        response. Useful when a search request contains multiple inner
        hits.
    :arg size: The maximum number of hits to return per `inner_hits`.
    :arg from: Inner hit starting document offset.
    :arg collapse: No documentation available.
    :arg docvalue_fields: No documentation available.
    :arg explain: No documentation available.
    :arg highlight: No documentation available.
    :arg ignore_unmapped: No documentation available.
    :arg script_fields: No documentation available.
    :arg seq_no_primary_term: No documentation available.
    :arg fields: No documentation available.
    :arg sort: How the inner hits should be sorted per `inner_hits`. By
        default, inner hits are sorted by score.
    :arg _source: No documentation available.
    :arg stored_fields: No documentation available.
    :arg track_scores: No documentation available.
    :arg version: No documentation available.
    """

    def __init__(
        self,
        *,
        name: Union[str, "NotSet"] = NOT_SET,
        size: Union[int, "NotSet"] = NOT_SET,
        from_: Union[int, "NotSet"] = NOT_SET,
        collapse: Union["i.FieldCollapse", Dict[str, Any], "NotSet"] = NOT_SET,
        docvalue_fields: Union[
            List["i.FieldAndFormat"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        explain: Union[bool, "NotSet"] = NOT_SET,
        highlight: Union["i.Highlight", Dict[str, Any], "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        script_fields: Union[
            Mapping[Union[str, "InstrumentedField"], "i.ScriptField"],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        seq_no_primary_term: Union[bool, "NotSet"] = NOT_SET,
        fields: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        sort: Union[
            Union[Union[str, "InstrumentedField"], "i.SortOptions"],
            List[Union[Union[str, "InstrumentedField"], "i.SortOptions"]],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        _source: Union[bool, "i.SourceFilter", Dict[str, Any], "NotSet"] = NOT_SET,
        stored_fields: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        track_scores: Union[bool, "NotSet"] = NOT_SET,
        version: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if name != NOT_SET:
            kwargs["name"] = name
        if size != NOT_SET:
            kwargs["size"] = size
        if from_ != NOT_SET:
            kwargs["from_"] = from_
        if collapse != NOT_SET:
            kwargs["collapse"] = collapse
        if docvalue_fields != NOT_SET:
            kwargs["docvalue_fields"] = docvalue_fields
        if explain != NOT_SET:
            kwargs["explain"] = explain
        if highlight != NOT_SET:
            kwargs["highlight"] = highlight
        if ignore_unmapped != NOT_SET:
            kwargs["ignore_unmapped"] = ignore_unmapped
        if script_fields != NOT_SET:
            kwargs["script_fields"] = str(script_fields)
        if seq_no_primary_term != NOT_SET:
            kwargs["seq_no_primary_term"] = seq_no_primary_term
        if fields != NOT_SET:
            kwargs["fields"] = str(fields)
        if sort != NOT_SET:
            kwargs["sort"] = str(sort)
        if _source != NOT_SET:
            kwargs["_source"] = _source
        if stored_fields != NOT_SET:
            kwargs["stored_fields"] = str(stored_fields)
        if track_scores != NOT_SET:
            kwargs["track_scores"] = track_scores
        if version != NOT_SET:
            kwargs["version"] = version
        super().__init__(kwargs)


class GeoDistanceFeatureQuery(DistanceFeatureQueryBase):
    pass


class SpanTermQuery(QueryBase):
    """
    :arg value: (required)No documentation available.
    """

    def __init__(self, *, value: Union[str, "NotSet"] = NOT_SET, **kwargs: Any):
        if value != NOT_SET:
            kwargs["value"] = value
        super().__init__(**kwargs)


class DateDistanceFeatureQuery(DistanceFeatureQueryBase):
    pass


class PinnedDoc(AttrDict[Any]):
    """
    :arg _id: (required)The unique document ID.
    :arg _index: (required)The index that contains the document.
    """

    def __init__(
        self,
        *,
        _id: Union[str, "NotSet"] = NOT_SET,
        _index: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if _id != NOT_SET:
            kwargs["_id"] = _id
        if _index != NOT_SET:
            kwargs["_index"] = _index
        super().__init__(kwargs)


class TermsSetQuery(QueryBase):
    """
    :arg minimum_should_match_field: Numeric field containing the number
        of matching terms required to return a document.
    :arg minimum_should_match_script: Custom script containing the number
        of matching terms required to return a document.
    :arg terms: (required)Array of terms you wish to find in the provided
        field.
    """

    def __init__(
        self,
        *,
        minimum_should_match_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        minimum_should_match_script: Union[
            "i.Script", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        terms: Union[List[str], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if minimum_should_match_field != NOT_SET:
            kwargs["minimum_should_match_field"] = str(minimum_should_match_field)
        if minimum_should_match_script != NOT_SET:
            kwargs["minimum_should_match_script"] = minimum_should_match_script
        if terms != NOT_SET:
            kwargs["terms"] = terms
        super().__init__(**kwargs)


class RankFeatureFunction(AttrDict[Any]):
    pass


class RankFeatureFunctionSaturation(RankFeatureFunction):
    """
    :arg pivot: Configurable pivot value so that the result will be less
        than 0.5.
    """

    def __init__(self, *, pivot: Union[float, "NotSet"] = NOT_SET, **kwargs: Any):
        if pivot != NOT_SET:
            kwargs["pivot"] = pivot
        super().__init__(**kwargs)


class RegexpQuery(QueryBase):
    """
    :arg case_insensitive: Allows case insensitive matching of the regular
        expression value with the indexed field values when set to `true`.
        When `false`, case sensitivity of matching depends on the
        underlying field’s mapping.
    :arg flags: Enables optional operators for the regular expression.
    :arg max_determinized_states: Maximum number of automaton states
        required for the query.
    :arg rewrite: Method used to rewrite the query.
    :arg value: (required)Regular expression for terms you wish to find in
        the provided field.
    """

    def __init__(
        self,
        *,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        flags: Union[str, "NotSet"] = NOT_SET,
        max_determinized_states: Union[int, "NotSet"] = NOT_SET,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        value: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if case_insensitive != NOT_SET:
            kwargs["case_insensitive"] = case_insensitive
        if flags != NOT_SET:
            kwargs["flags"] = flags
        if max_determinized_states != NOT_SET:
            kwargs["max_determinized_states"] = max_determinized_states
        if rewrite != NOT_SET:
            kwargs["rewrite"] = rewrite
        if value != NOT_SET:
            kwargs["value"] = value
        super().__init__(**kwargs)


class MatchBoolPrefixQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert the text in the query value
        into tokens.
    :arg fuzziness: Maximum edit distance allowed for matching. Can be
        applied to the term subqueries constructed for all terms but the
        final term.
    :arg fuzzy_rewrite: Method used to rewrite the query. Can be applied
        to the term subqueries constructed for all terms but the final
        term.
    :arg fuzzy_transpositions: If `true`, edits for fuzzy matching include
        transpositions of two adjacent characters (for example, `ab` to
        `ba`). Can be applied to the term subqueries constructed for all
        terms but the final term.
    :arg max_expansions: Maximum number of terms to which the query will
        expand. Can be applied to the term subqueries constructed for all
        terms but the final term.
    :arg minimum_should_match: Minimum number of clauses that must match
        for a document to be returned. Applied to the constructed bool
        query.
    :arg operator: Boolean logic used to interpret text in the query
        value. Applied to the constructed bool query.
    :arg prefix_length: Number of beginning characters left unchanged for
        fuzzy matching. Can be applied to the term subqueries constructed
        for all terms but the final term.
    :arg query: (required)Terms you wish to find in the provided field.
        The last term is used in a prefix query.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        fuzzy_rewrite: Union[str, "NotSet"] = NOT_SET,
        fuzzy_transpositions: Union[bool, "NotSet"] = NOT_SET,
        max_expansions: Union[int, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        prefix_length: Union[int, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if fuzziness != NOT_SET:
            kwargs["fuzziness"] = fuzziness
        if fuzzy_rewrite != NOT_SET:
            kwargs["fuzzy_rewrite"] = fuzzy_rewrite
        if fuzzy_transpositions != NOT_SET:
            kwargs["fuzzy_transpositions"] = fuzzy_transpositions
        if max_expansions != NOT_SET:
            kwargs["max_expansions"] = max_expansions
        if minimum_should_match != NOT_SET:
            kwargs["minimum_should_match"] = minimum_should_match
        if operator != NOT_SET:
            kwargs["operator"] = operator
        if prefix_length != NOT_SET:
            kwargs["prefix_length"] = prefix_length
        if query != NOT_SET:
            kwargs["query"] = query
        super().__init__(**kwargs)


class FuzzyQuery(QueryBase):
    """
    :arg max_expansions: Maximum number of variations created.
    :arg prefix_length: Number of beginning characters left unchanged when
        creating expansions.
    :arg rewrite: Number of beginning characters left unchanged when
        creating expansions.
    :arg transpositions: Indicates whether edits include transpositions of
        two adjacent characters (for example `ab` to `ba`).
    :arg fuzziness: Maximum edit distance allowed for matching.
    :arg value: (required)Term you wish to find in the provided field.
    """

    def __init__(
        self,
        *,
        max_expansions: Union[int, "NotSet"] = NOT_SET,
        prefix_length: Union[int, "NotSet"] = NOT_SET,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        transpositions: Union[bool, "NotSet"] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        value: Union[str, float, bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if max_expansions != NOT_SET:
            kwargs["max_expansions"] = max_expansions
        if prefix_length != NOT_SET:
            kwargs["prefix_length"] = prefix_length
        if rewrite != NOT_SET:
            kwargs["rewrite"] = rewrite
        if transpositions != NOT_SET:
            kwargs["transpositions"] = transpositions
        if fuzziness != NOT_SET:
            kwargs["fuzziness"] = fuzziness
        if value != NOT_SET:
            kwargs["value"] = value
        super().__init__(**kwargs)


class MatchPhraseQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert the text in the query value
        into tokens.
    :arg query: (required)Query terms that are analyzed and turned into a
        phrase query.
    :arg slop: Maximum number of positions allowed between matching
        tokens.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the `analyzer` removes all tokens, such as when using a `stop`
        filter.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        zero_terms_query: Union[Literal["all", "none"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if query != NOT_SET:
            kwargs["query"] = query
        if slop != NOT_SET:
            kwargs["slop"] = slop
        if zero_terms_query != NOT_SET:
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


class WildcardQuery(QueryBase):
    """
    :arg case_insensitive: Allows case insensitive matching of the pattern
        with the indexed field values when set to true. Default is false
        which means the case sensitivity of matching depends on the
        underlying field’s mapping.
    :arg rewrite: Method used to rewrite the query.
    :arg value: Wildcard pattern for terms you wish to find in the
        provided field. Required, when wildcard is not set.
    :arg wildcard: Wildcard pattern for terms you wish to find in the
        provided field. Required, when value is not set.
    """

    def __init__(
        self,
        *,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        value: Union[str, "NotSet"] = NOT_SET,
        wildcard: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if case_insensitive != NOT_SET:
            kwargs["case_insensitive"] = case_insensitive
        if rewrite != NOT_SET:
            kwargs["rewrite"] = rewrite
        if value != NOT_SET:
            kwargs["value"] = value
        if wildcard != NOT_SET:
            kwargs["wildcard"] = wildcard
        super().__init__(**kwargs)


class RankFeatureFunctionLogarithm(RankFeatureFunction):
    """
    :arg scaling_factor: (required)Configurable scaling factor.
    """

    def __init__(
        self, *, scaling_factor: Union[float, "NotSet"] = NOT_SET, **kwargs: Any
    ):
        if scaling_factor != NOT_SET:
            kwargs["scaling_factor"] = scaling_factor
        super().__init__(**kwargs)


class MatchPhrasePrefixQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert text in the query value into
        tokens.
    :arg max_expansions: Maximum number of terms to which the last
        provided term of the query value will expand.
    :arg query: (required)Text you wish to find in the provided field.
    :arg slop: Maximum number of positions allowed between matching
        tokens.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the analyzer removes all tokens, such as when using a `stop`
        filter.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        max_expansions: Union[int, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        zero_terms_query: Union[Literal["all", "none"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if max_expansions != NOT_SET:
            kwargs["max_expansions"] = max_expansions
        if query != NOT_SET:
            kwargs["query"] = query
        if slop != NOT_SET:
            kwargs["slop"] = slop
        if zero_terms_query != NOT_SET:
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


class TokenPruningConfig(AttrDict[Any]):
    """
    :arg tokens_freq_ratio_threshold: Tokens whose frequency is more than
        this threshold times the average frequency of all tokens in the
        specified field are considered outliers and pruned.
    :arg tokens_weight_threshold: Tokens whose weight is less than this
        threshold are considered nonsignificant and pruned.
    :arg only_score_pruned_tokens: Whether to only score pruned tokens, vs
        only scoring kept tokens.
    """

    def __init__(
        self,
        *,
        tokens_freq_ratio_threshold: Union[int, "NotSet"] = NOT_SET,
        tokens_weight_threshold: Union[float, "NotSet"] = NOT_SET,
        only_score_pruned_tokens: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if tokens_freq_ratio_threshold != NOT_SET:
            kwargs["tokens_freq_ratio_threshold"] = tokens_freq_ratio_threshold
        if tokens_weight_threshold != NOT_SET:
            kwargs["tokens_weight_threshold"] = tokens_weight_threshold
        if only_score_pruned_tokens != NOT_SET:
            kwargs["only_score_pruned_tokens"] = only_score_pruned_tokens
        super().__init__(kwargs)


class FunctionScoreContainer(AttrDict[Any]):
    """
    :arg exp: Function that scores a document with a exponential decay,
        depending on the distance of a numeric field value of the document
        from an origin.
    :arg gauss: Function that scores a document with a normal decay,
        depending on the distance of a numeric field value of the document
        from an origin.
    :arg linear: Function that scores a document with a linear decay,
        depending on the distance of a numeric field value of the document
        from an origin.
    :arg field_value_factor: Function allows you to use a field from a
        document to influence the score. It’s similar to using the
        script_score function, however, it avoids the overhead of
        scripting.
    :arg random_score: Generates scores that are uniformly distributed
        from 0 up to but not including 1. In case you want scores to be
        reproducible, it is possible to provide a `seed` and `field`.
    :arg script_score: Enables you to wrap another query and customize the
        scoring of it optionally with a computation derived from other
        numeric field values in the doc using a script expression.
    :arg filter: No documentation available.
    :arg weight: No documentation available.
    """

    def __init__(
        self,
        *,
        exp: Union[
            "f.UntypedDecayFunction",
            "f.DateDecayFunction",
            "f.NumericDecayFunction",
            "f.GeoDecayFunction",
            "NotSet",
        ] = NOT_SET,
        gauss: Union[
            "f.UntypedDecayFunction",
            "f.DateDecayFunction",
            "f.NumericDecayFunction",
            "f.GeoDecayFunction",
            "NotSet",
        ] = NOT_SET,
        linear: Union[
            "f.UntypedDecayFunction",
            "f.DateDecayFunction",
            "f.NumericDecayFunction",
            "f.GeoDecayFunction",
            "NotSet",
        ] = NOT_SET,
        field_value_factor: Union[
            "f.FieldValueFactorScoreFunction", "NotSet"
        ] = NOT_SET,
        random_score: Union["f.RandomScoreFunction", "NotSet"] = NOT_SET,
        script_score: Union["f.ScriptScoreFunction", "NotSet"] = NOT_SET,
        filter: Union[Query, "NotSet"] = NOT_SET,
        weight: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if exp != NOT_SET:
            kwargs["exp"] = exp
        if gauss != NOT_SET:
            kwargs["gauss"] = gauss
        if linear != NOT_SET:
            kwargs["linear"] = linear
        if field_value_factor != NOT_SET:
            kwargs["field_value_factor"] = field_value_factor
        if random_score != NOT_SET:
            kwargs["random_score"] = random_score
        if script_score != NOT_SET:
            kwargs["script_score"] = script_score
        if filter != NOT_SET:
            kwargs["filter"] = filter
        if weight != NOT_SET:
            kwargs["weight"] = weight
        super().__init__(kwargs)


class IntervalsQuery(QueryBase):
    """
    :arg all_of: Returns matches that span a combination of other rules.
    :arg any_of: Returns intervals produced by any of its sub-rules.
    :arg fuzzy: Matches terms that are similar to the provided term,
        within an edit distance defined by `fuzziness`.
    :arg match: Matches analyzed text.
    :arg prefix: Matches terms that start with a specified set of
        characters.
    :arg wildcard: Matches terms using a wildcard pattern.
    """

    def __init__(
        self,
        *,
        all_of: Union["i.IntervalsAllOf", Dict[str, Any], "NotSet"] = NOT_SET,
        any_of: Union["i.IntervalsAnyOf", Dict[str, Any], "NotSet"] = NOT_SET,
        fuzzy: Union["i.IntervalsFuzzy", Dict[str, Any], "NotSet"] = NOT_SET,
        match: Union["i.IntervalsMatch", Dict[str, Any], "NotSet"] = NOT_SET,
        prefix: Union["i.IntervalsPrefix", Dict[str, Any], "NotSet"] = NOT_SET,
        wildcard: Union["i.IntervalsWildcard", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if all_of != NOT_SET:
            kwargs["all_of"] = all_of
        if any_of != NOT_SET:
            kwargs["any_of"] = any_of
        if fuzzy != NOT_SET:
            kwargs["fuzzy"] = fuzzy
        if match != NOT_SET:
            kwargs["match"] = match
        if prefix != NOT_SET:
            kwargs["prefix"] = prefix
        if wildcard != NOT_SET:
            kwargs["wildcard"] = wildcard
        super().__init__(**kwargs)


class RankFeatureFunctionLinear(RankFeatureFunction):
    pass


class MatchQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert the text in the query value
        into tokens.
    :arg auto_generate_synonyms_phrase_query: If `true`, match phrase
        queries are automatically created for multi-term synonyms.
    :arg cutoff_frequency: No documentation available.
    :arg fuzziness: Maximum edit distance allowed for matching.
    :arg fuzzy_rewrite: Method used to rewrite the query.
    :arg fuzzy_transpositions: If `true`, edits for fuzzy matching include
        transpositions of two adjacent characters (for example, `ab` to
        `ba`).
    :arg lenient: If `true`, format-based errors, such as providing a text
        query value for a numeric field, are ignored.
    :arg max_expansions: Maximum number of terms to which the query will
        expand.
    :arg minimum_should_match: Minimum number of clauses that must match
        for a document to be returned.
    :arg operator: Boolean logic used to interpret text in the query
        value.
    :arg prefix_length: Number of beginning characters left unchanged for
        fuzzy matching.
    :arg query: (required)Text, number, boolean value or date you wish to
        find in the provided field.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the `analyzer` removes all tokens, such as when using a `stop`
        filter.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        auto_generate_synonyms_phrase_query: Union[bool, "NotSet"] = NOT_SET,
        cutoff_frequency: Union[float, "NotSet"] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        fuzzy_rewrite: Union[str, "NotSet"] = NOT_SET,
        fuzzy_transpositions: Union[bool, "NotSet"] = NOT_SET,
        lenient: Union[bool, "NotSet"] = NOT_SET,
        max_expansions: Union[int, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        prefix_length: Union[int, "NotSet"] = NOT_SET,
        query: Union[str, float, bool, "NotSet"] = NOT_SET,
        zero_terms_query: Union[Literal["all", "none"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if auto_generate_synonyms_phrase_query != NOT_SET:
            kwargs["auto_generate_synonyms_phrase_query"] = (
                auto_generate_synonyms_phrase_query
            )
        if cutoff_frequency != NOT_SET:
            kwargs["cutoff_frequency"] = cutoff_frequency
        if fuzziness != NOT_SET:
            kwargs["fuzziness"] = fuzziness
        if fuzzy_rewrite != NOT_SET:
            kwargs["fuzzy_rewrite"] = fuzzy_rewrite
        if fuzzy_transpositions != NOT_SET:
            kwargs["fuzzy_transpositions"] = fuzzy_transpositions
        if lenient != NOT_SET:
            kwargs["lenient"] = lenient
        if max_expansions != NOT_SET:
            kwargs["max_expansions"] = max_expansions
        if minimum_should_match != NOT_SET:
            kwargs["minimum_should_match"] = minimum_should_match
        if operator != NOT_SET:
            kwargs["operator"] = operator
        if prefix_length != NOT_SET:
            kwargs["prefix_length"] = prefix_length
        if query != NOT_SET:
            kwargs["query"] = query
        if zero_terms_query != NOT_SET:
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


class WeightedTokensQuery(QueryBase):
    """
    :arg tokens: (required)The tokens representing this query
    :arg pruning_config: Token pruning configurations
    """

    def __init__(
        self,
        *,
        tokens: Union[Mapping[str, float], "NotSet"] = NOT_SET,
        pruning_config: Union[
            "i.TokenPruningConfig", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if tokens != NOT_SET:
            kwargs["tokens"] = tokens
        if pruning_config != NOT_SET:
            kwargs["pruning_config"] = pruning_config
        super().__init__(**kwargs)


class LikeDocument(AttrDict[Any]):
    """
    :arg doc: A document not present in the index.
    :arg fields: No documentation available.
    :arg _id: ID of a document.
    :arg _index: Index of a document.
    :arg per_field_analyzer: Overrides the default analyzer.
    :arg routing: No documentation available.
    :arg version: No documentation available.
    :arg version_type: No documentation available.
    """

    def __init__(
        self,
        *,
        doc: Any = NOT_SET,
        fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"] = NOT_SET,
        _id: Union[str, "NotSet"] = NOT_SET,
        _index: Union[str, "NotSet"] = NOT_SET,
        per_field_analyzer: Union[
            Mapping[Union[str, "InstrumentedField"], str], "NotSet"
        ] = NOT_SET,
        routing: Union[str, "NotSet"] = NOT_SET,
        version: Union[int, "NotSet"] = NOT_SET,
        version_type: Union[
            Literal["internal", "external", "external_gte", "force"], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if doc != NOT_SET:
            kwargs["doc"] = doc
        if fields != NOT_SET:
            kwargs["fields"] = str(fields)
        if _id != NOT_SET:
            kwargs["_id"] = _id
        if _index != NOT_SET:
            kwargs["_index"] = _index
        if per_field_analyzer != NOT_SET:
            kwargs["per_field_analyzer"] = str(per_field_analyzer)
        if routing != NOT_SET:
            kwargs["routing"] = routing
        if version != NOT_SET:
            kwargs["version"] = version
        if version_type != NOT_SET:
            kwargs["version_type"] = version_type
        super().__init__(kwargs)


class SpanQuery(AttrDict[Any]):
    """
    :arg span_containing: Accepts a list of span queries, but only returns
        those spans which also match a second span query.
    :arg span_field_masking: Allows queries like `span_near` or `span_or`
        across different fields.
    :arg span_first: Accepts another span query whose matches must appear
        within the first N positions of the field.
    :arg span_gap: No documentation available.
    :arg span_multi: Wraps a `term`, `range`, `prefix`, `wildcard`,
        `regexp`, or `fuzzy` query.
    :arg span_near: Accepts multiple span queries whose matches must be
        within the specified distance of each other, and possibly in the
        same order.
    :arg span_not: Wraps another span query, and excludes any documents
        which match that query.
    :arg span_or: Combines multiple span queries and returns documents
        which match any of the specified queries.
    :arg span_term: The equivalent of the `term` query but for use with
        other span queries.
    :arg span_within: The result from a single span query is returned as
        long is its span falls within the spans returned by a list of
        other span queries.
    """

    def __init__(
        self,
        *,
        span_containing: Union[
            "i.SpanContainingQuery", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        span_field_masking: Union[
            "i.SpanFieldMaskingQuery", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        span_first: Union["i.SpanFirstQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        span_gap: Union[
            Mapping[Union[str, "InstrumentedField"], int], "NotSet"
        ] = NOT_SET,
        span_multi: Union["i.SpanMultiTermQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        span_near: Union["i.SpanNearQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        span_not: Union["i.SpanNotQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        span_or: Union["i.SpanOrQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        span_term: Union[
            Mapping[Union[str, "InstrumentedField"], "i.SpanTermQuery"],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        span_within: Union["i.SpanWithinQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if span_containing != NOT_SET:
            kwargs["span_containing"] = span_containing
        if span_field_masking != NOT_SET:
            kwargs["span_field_masking"] = span_field_masking
        if span_first != NOT_SET:
            kwargs["span_first"] = span_first
        if span_gap != NOT_SET:
            kwargs["span_gap"] = str(span_gap)
        if span_multi != NOT_SET:
            kwargs["span_multi"] = span_multi
        if span_near != NOT_SET:
            kwargs["span_near"] = span_near
        if span_not != NOT_SET:
            kwargs["span_not"] = span_not
        if span_or != NOT_SET:
            kwargs["span_or"] = span_or
        if span_term != NOT_SET:
            kwargs["span_term"] = str(span_term)
        if span_within != NOT_SET:
            kwargs["span_within"] = span_within
        super().__init__(kwargs)


class PrefixQuery(QueryBase):
    """
    :arg rewrite: Method used to rewrite the query.
    :arg value: (required)Beginning characters of terms you wish to find
        in the provided field.
    :arg case_insensitive: Allows ASCII case insensitive matching of the
        value with the indexed field values when set to `true`. Default is
        `false` which means the case sensitivity of matching depends on
        the underlying field’s mapping.
    """

    def __init__(
        self,
        *,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        value: Union[str, "NotSet"] = NOT_SET,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if rewrite != NOT_SET:
            kwargs["rewrite"] = rewrite
        if value != NOT_SET:
            kwargs["value"] = value
        if case_insensitive != NOT_SET:
            kwargs["case_insensitive"] = case_insensitive
        super().__init__(**kwargs)


class RankFeatureFunctionSigmoid(RankFeatureFunction):
    """
    :arg pivot: (required)Configurable pivot value so that the result will
        be less than 0.5.
    :arg exponent: (required)Configurable Exponent.
    """

    def __init__(
        self,
        *,
        pivot: Union[float, "NotSet"] = NOT_SET,
        exponent: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if pivot != NOT_SET:
            kwargs["pivot"] = pivot
        if exponent != NOT_SET:
            kwargs["exponent"] = exponent
        super().__init__(**kwargs)


class CommonTermsQuery(QueryBase):
    """
    :arg analyzer: No documentation available.
    :arg cutoff_frequency: No documentation available.
    :arg high_freq_operator: No documentation available.
    :arg low_freq_operator: No documentation available.
    :arg minimum_should_match: No documentation available.
    :arg query: (required)No documentation available.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        cutoff_frequency: Union[float, "NotSet"] = NOT_SET,
        high_freq_operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        low_freq_operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if cutoff_frequency != NOT_SET:
            kwargs["cutoff_frequency"] = cutoff_frequency
        if high_freq_operator != NOT_SET:
            kwargs["high_freq_operator"] = high_freq_operator
        if low_freq_operator != NOT_SET:
            kwargs["low_freq_operator"] = low_freq_operator
        if minimum_should_match != NOT_SET:
            kwargs["minimum_should_match"] = minimum_should_match
        if query != NOT_SET:
            kwargs["query"] = query
        super().__init__(**kwargs)


class Script(AttrDict[Any]):
    """
    :arg source: The script source.
    :arg id: The `id` for a stored script.
    :arg params: Specifies any named parameters that are passed into the
        script as variables. Use parameters instead of hard-coded values
        to decrease compile time.
    :arg lang: Specifies the language the script is written in.
    :arg options: No documentation available.
    """

    def __init__(
        self,
        *,
        source: Union[str, "NotSet"] = NOT_SET,
        id: Union[str, "NotSet"] = NOT_SET,
        params: Union[Mapping[str, Any], "NotSet"] = NOT_SET,
        lang: Union[
            Literal["painless", "expression", "mustache", "java"], "NotSet"
        ] = NOT_SET,
        options: Union[Mapping[str, str], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if source != NOT_SET:
            kwargs["source"] = source
        if id != NOT_SET:
            kwargs["id"] = id
        if params != NOT_SET:
            kwargs["params"] = params
        if lang != NOT_SET:
            kwargs["lang"] = lang
        if options != NOT_SET:
            kwargs["options"] = options
        super().__init__(kwargs)


class TextEmbedding(AttrDict[Any]):
    """
    :arg model_id: (required)No documentation available.
    :arg model_text: (required)No documentation available.
    """

    def __init__(
        self,
        *,
        model_id: Union[str, "NotSet"] = NOT_SET,
        model_text: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if model_id != NOT_SET:
            kwargs["model_id"] = model_id
        if model_text != NOT_SET:
            kwargs["model_text"] = model_text
        super().__init__(kwargs)


class HighlightBase(AttrDict[Any]):
    """
    :arg type: No documentation available.
    :arg boundary_chars: A string that contains each boundary character.
    :arg boundary_max_scan: How far to scan for boundary characters.
    :arg boundary_scanner: Specifies how to break the highlighted
        fragments: chars, sentence, or word. Only valid for the unified
        and fvh highlighters. Defaults to `sentence` for the `unified`
        highlighter. Defaults to `chars` for the `fvh` highlighter.
    :arg boundary_scanner_locale: Controls which locale is used to search
        for sentence and word boundaries. This parameter takes a form of a
        language tag, for example: `"en-US"`, `"fr-FR"`, `"ja-JP"`.
    :arg force_source: No documentation available.
    :arg fragmenter: Specifies how text should be broken up in highlight
        snippets: `simple` or `span`. Only valid for the `plain`
        highlighter.
    :arg fragment_size: The size of the highlighted fragment in
        characters.
    :arg highlight_filter: No documentation available.
    :arg highlight_query: Highlight matches for a query other than the
        search query. This is especially useful if you use a rescore query
        because those are not taken into account by highlighting by
        default.
    :arg max_fragment_length: No documentation available.
    :arg max_analyzed_offset: If set to a non-negative value, highlighting
        stops at this defined maximum limit. The rest of the text is not
        processed, thus not highlighted and no error is returned The
        `max_analyzed_offset` query setting does not override the
        `index.highlight.max_analyzed_offset` setting, which prevails when
        it’s set to lower value than the query setting.
    :arg no_match_size: The amount of text you want to return from the
        beginning of the field if there are no matching fragments to
        highlight.
    :arg number_of_fragments: The maximum number of fragments to return.
        If the number of fragments is set to `0`, no fragments are
        returned. Instead, the entire field contents are highlighted and
        returned. This can be handy when you need to highlight short texts
        such as a title or address, but fragmentation is not required. If
        `number_of_fragments` is `0`, `fragment_size` is ignored.
    :arg options: No documentation available.
    :arg order: Sorts highlighted fragments by score when set to `score`.
        By default, fragments will be output in the order they appear in
        the field (order: `none`). Setting this option to `score` will
        output the most relevant fragments first. Each highlighter applies
        its own logic to compute relevancy scores.
    :arg phrase_limit: Controls the number of matching phrases in a
        document that are considered. Prevents the `fvh` highlighter from
        analyzing too many phrases and consuming too much memory. When
        using `matched_fields`, `phrase_limit` phrases per matched field
        are considered. Raising the limit increases query time and
        consumes more memory. Only supported by the `fvh` highlighter.
    :arg post_tags: Use in conjunction with `pre_tags` to define the HTML
        tags to use for the highlighted text. By default, highlighted text
        is wrapped in `<em>` and `</em>` tags.
    :arg pre_tags: Use in conjunction with `post_tags` to define the HTML
        tags to use for the highlighted text. By default, highlighted text
        is wrapped in `<em>` and `</em>` tags.
    :arg require_field_match: By default, only fields that contains a
        query match are highlighted. Set to `false` to highlight all
        fields.
    :arg tags_schema: Set to `styled` to use the built-in tag schema.
    """

    def __init__(
        self,
        *,
        type: Union[Literal["plain", "fvh", "unified"], "NotSet"] = NOT_SET,
        boundary_chars: Union[str, "NotSet"] = NOT_SET,
        boundary_max_scan: Union[int, "NotSet"] = NOT_SET,
        boundary_scanner: Union[
            Literal["chars", "sentence", "word"], "NotSet"
        ] = NOT_SET,
        boundary_scanner_locale: Union[str, "NotSet"] = NOT_SET,
        force_source: Union[bool, "NotSet"] = NOT_SET,
        fragmenter: Union[Literal["simple", "span"], "NotSet"] = NOT_SET,
        fragment_size: Union[int, "NotSet"] = NOT_SET,
        highlight_filter: Union[bool, "NotSet"] = NOT_SET,
        highlight_query: Union[Query, "NotSet"] = NOT_SET,
        max_fragment_length: Union[int, "NotSet"] = NOT_SET,
        max_analyzed_offset: Union[int, "NotSet"] = NOT_SET,
        no_match_size: Union[int, "NotSet"] = NOT_SET,
        number_of_fragments: Union[int, "NotSet"] = NOT_SET,
        options: Union[Mapping[str, Any], "NotSet"] = NOT_SET,
        order: Union[Literal["score"], "NotSet"] = NOT_SET,
        phrase_limit: Union[int, "NotSet"] = NOT_SET,
        post_tags: Union[List[str], "NotSet"] = NOT_SET,
        pre_tags: Union[List[str], "NotSet"] = NOT_SET,
        require_field_match: Union[bool, "NotSet"] = NOT_SET,
        tags_schema: Union[Literal["styled"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if type != NOT_SET:
            kwargs["type"] = type
        if boundary_chars != NOT_SET:
            kwargs["boundary_chars"] = boundary_chars
        if boundary_max_scan != NOT_SET:
            kwargs["boundary_max_scan"] = boundary_max_scan
        if boundary_scanner != NOT_SET:
            kwargs["boundary_scanner"] = boundary_scanner
        if boundary_scanner_locale != NOT_SET:
            kwargs["boundary_scanner_locale"] = boundary_scanner_locale
        if force_source != NOT_SET:
            kwargs["force_source"] = force_source
        if fragmenter != NOT_SET:
            kwargs["fragmenter"] = fragmenter
        if fragment_size != NOT_SET:
            kwargs["fragment_size"] = fragment_size
        if highlight_filter != NOT_SET:
            kwargs["highlight_filter"] = highlight_filter
        if highlight_query != NOT_SET:
            kwargs["highlight_query"] = highlight_query
        if max_fragment_length != NOT_SET:
            kwargs["max_fragment_length"] = max_fragment_length
        if max_analyzed_offset != NOT_SET:
            kwargs["max_analyzed_offset"] = max_analyzed_offset
        if no_match_size != NOT_SET:
            kwargs["no_match_size"] = no_match_size
        if number_of_fragments != NOT_SET:
            kwargs["number_of_fragments"] = number_of_fragments
        if options != NOT_SET:
            kwargs["options"] = options
        if order != NOT_SET:
            kwargs["order"] = order
        if phrase_limit != NOT_SET:
            kwargs["phrase_limit"] = phrase_limit
        if post_tags != NOT_SET:
            kwargs["post_tags"] = post_tags
        if pre_tags != NOT_SET:
            kwargs["pre_tags"] = pre_tags
        if require_field_match != NOT_SET:
            kwargs["require_field_match"] = require_field_match
        if tags_schema != NOT_SET:
            kwargs["tags_schema"] = tags_schema
        super().__init__(kwargs)


class Highlight(HighlightBase):
    """
    :arg encoder: No documentation available.
    :arg fields: (required)No documentation available.
    """

    def __init__(
        self,
        *,
        encoder: Union[Literal["default", "html"], "NotSet"] = NOT_SET,
        fields: Union[
            Mapping[Union[str, "InstrumentedField"], "i.HighlightField"],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if encoder != NOT_SET:
            kwargs["encoder"] = encoder
        if fields != NOT_SET:
            kwargs["fields"] = str(fields)
        super().__init__(**kwargs)


class FieldCollapse(AttrDict[Any]):
    """
    :arg field: (required)The field to collapse the result set on
    :arg inner_hits: The number of inner hits and their sort order
    :arg max_concurrent_group_searches: The number of concurrent requests
        allowed to retrieve the inner_hits per group
    :arg collapse: No documentation available.
    """

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        inner_hits: Union[
            "i.InnerHits", List["i.InnerHits"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        max_concurrent_group_searches: Union[int, "NotSet"] = NOT_SET,
        collapse: Union["i.FieldCollapse", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if field != NOT_SET:
            kwargs["field"] = str(field)
        if inner_hits != NOT_SET:
            kwargs["inner_hits"] = inner_hits
        if max_concurrent_group_searches != NOT_SET:
            kwargs["max_concurrent_group_searches"] = max_concurrent_group_searches
        if collapse != NOT_SET:
            kwargs["collapse"] = collapse
        super().__init__(kwargs)


class FieldAndFormat(AttrDict[Any]):
    """
    :arg field: (required)Wildcard pattern. The request returns values for
        field names matching this pattern.
    :arg format: Format in which the values are returned.
    :arg include_unmapped: No documentation available.
    """

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        format: Union[str, "NotSet"] = NOT_SET,
        include_unmapped: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if field != NOT_SET:
            kwargs["field"] = str(field)
        if format != NOT_SET:
            kwargs["format"] = format
        if include_unmapped != NOT_SET:
            kwargs["include_unmapped"] = include_unmapped
        super().__init__(kwargs)


class SourceFilter(AttrDict[Any]):
    """
    :arg excludes: No documentation available.
    :arg includes: No documentation available.
    """

    def __init__(
        self,
        *,
        excludes: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        includes: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if excludes != NOT_SET:
            kwargs["excludes"] = str(excludes)
        if includes != NOT_SET:
            kwargs["includes"] = str(includes)
        super().__init__(kwargs)


class ScriptField(AttrDict[Any]):
    """
    :arg script: (required)No documentation available.
    :arg ignore_failure: No documentation available.
    """

    def __init__(
        self,
        *,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        ignore_failure: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if script != NOT_SET:
            kwargs["script"] = script
        if ignore_failure != NOT_SET:
            kwargs["ignore_failure"] = ignore_failure
        super().__init__(kwargs)


class SortOptions(AttrDict[Any]):
    """
    :arg _score: No documentation available.
    :arg _doc: No documentation available.
    :arg _geo_distance: No documentation available.
    :arg _script: No documentation available.
    """

    def __init__(
        self,
        *,
        _score: Union["i.ScoreSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _doc: Union["i.ScoreSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _geo_distance: Union["i.GeoDistanceSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _script: Union["i.ScriptSort", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if _score != NOT_SET:
            kwargs["_score"] = _score
        if _doc != NOT_SET:
            kwargs["_doc"] = _doc
        if _geo_distance != NOT_SET:
            kwargs["_geo_distance"] = _geo_distance
        if _script != NOT_SET:
            kwargs["_script"] = _script
        super().__init__(kwargs)


class IntervalsFuzzy(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to normalize the term.
    :arg fuzziness: Maximum edit distance allowed for matching.
    :arg prefix_length: Number of beginning characters left unchanged when
        creating expansions.
    :arg term: (required)The term to match.
    :arg transpositions: Indicates whether edits include transpositions of
        two adjacent characters (for example, `ab` to `ba`).
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `term` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        prefix_length: Union[int, "NotSet"] = NOT_SET,
        term: Union[str, "NotSet"] = NOT_SET,
        transpositions: Union[bool, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if fuzziness != NOT_SET:
            kwargs["fuzziness"] = fuzziness
        if prefix_length != NOT_SET:
            kwargs["prefix_length"] = prefix_length
        if term != NOT_SET:
            kwargs["term"] = term
        if transpositions != NOT_SET:
            kwargs["transpositions"] = transpositions
        if use_field != NOT_SET:
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class IntervalsAllOf(AttrDict[Any]):
    """
    :arg intervals: (required)An array of rules to combine. All rules must
        produce a match in a document for the overall source to match.
    :arg max_gaps: Maximum number of positions between the matching terms.
        Intervals produced by the rules further apart than this are not
        considered matches.
    :arg ordered: If `true`, intervals produced by the rules should appear
        in the order in which they are specified.
    :arg filter: Rule used to filter returned intervals.
    """

    def __init__(
        self,
        *,
        intervals: Union[
            List["i.IntervalsContainer"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        max_gaps: Union[int, "NotSet"] = NOT_SET,
        ordered: Union[bool, "NotSet"] = NOT_SET,
        filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if intervals != NOT_SET:
            kwargs["intervals"] = intervals
        if max_gaps != NOT_SET:
            kwargs["max_gaps"] = max_gaps
        if ordered != NOT_SET:
            kwargs["ordered"] = ordered
        if filter != NOT_SET:
            kwargs["filter"] = filter
        super().__init__(kwargs)


class IntervalsMatch(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze terms in the query.
    :arg max_gaps: Maximum number of positions between the matching terms.
        Terms further apart than this are not considered matches.
    :arg ordered: If `true`, matching terms must appear in their specified
        order.
    :arg query: (required)Text you wish to find in the provided field.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `term` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    :arg filter: An optional interval filter.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        max_gaps: Union[int, "NotSet"] = NOT_SET,
        ordered: Union[bool, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if max_gaps != NOT_SET:
            kwargs["max_gaps"] = max_gaps
        if ordered != NOT_SET:
            kwargs["ordered"] = ordered
        if query != NOT_SET:
            kwargs["query"] = query
        if use_field != NOT_SET:
            kwargs["use_field"] = str(use_field)
        if filter != NOT_SET:
            kwargs["filter"] = filter
        super().__init__(kwargs)


class IntervalsPrefix(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze the `prefix`.
    :arg prefix: (required)Beginning characters of terms you wish to find
        in the top-level field.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `prefix` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        prefix: Union[str, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if prefix != NOT_SET:
            kwargs["prefix"] = prefix
        if use_field != NOT_SET:
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class IntervalsWildcard(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze the `pattern`. Defaults to the
        top-level field's analyzer.
    :arg pattern: (required)Wildcard pattern used to find matching terms.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `pattern` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        pattern: Union[str, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        if pattern != NOT_SET:
            kwargs["pattern"] = pattern
        if use_field != NOT_SET:
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class IntervalsAnyOf(AttrDict[Any]):
    """
    :arg intervals: (required)An array of rules to match.
    :arg filter: Rule used to filter returned intervals.
    """

    def __init__(
        self,
        *,
        intervals: Union[
            List["i.IntervalsContainer"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if intervals != NOT_SET:
            kwargs["intervals"] = intervals
        if filter != NOT_SET:
            kwargs["filter"] = filter
        super().__init__(kwargs)


class SpanFieldMaskingQuery(QueryBase):
    """
    :arg field: (required)No documentation available.
    :arg query: (required)No documentation available.
    """

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        query: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if field != NOT_SET:
            kwargs["field"] = str(field)
        if query != NOT_SET:
            kwargs["query"] = query
        super().__init__(**kwargs)


class SpanNearQuery(QueryBase):
    """
    :arg clauses: (required)Array of one or more other span type queries.
    :arg in_order: Controls whether matches are required to be in-order.
    :arg slop: Controls the maximum number of intervening unmatched
        positions permitted.
    """

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        in_order: Union[bool, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if clauses != NOT_SET:
            kwargs["clauses"] = clauses
        if in_order != NOT_SET:
            kwargs["in_order"] = in_order
        if slop != NOT_SET:
            kwargs["slop"] = slop
        super().__init__(**kwargs)


class SpanMultiTermQuery(QueryBase):
    """
    :arg match: (required)Should be a multi term query (one of `wildcard`,
        `fuzzy`, `prefix`, `range`, or `regexp` query).
    """

    def __init__(self, *, match: Union[Query, "NotSet"] = NOT_SET, **kwargs: Any):
        if match != NOT_SET:
            kwargs["match"] = match
        super().__init__(**kwargs)


class SpanContainingQuery(QueryBase):
    """
    :arg big: (required)Can be any span query. Matching spans from `big`
        that contain matches from `little` are returned.
    :arg little: (required)Can be any span query. Matching spans from
        `big` that contain matches from `little` are returned.
    """

    def __init__(
        self,
        *,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if big != NOT_SET:
            kwargs["big"] = big
        if little != NOT_SET:
            kwargs["little"] = little
        super().__init__(**kwargs)


class SpanFirstQuery(QueryBase):
    """
    :arg end: (required)Controls the maximum end position permitted in a
        match.
    :arg match: (required)Can be any other span type query.
    """

    def __init__(
        self,
        *,
        end: Union[int, "NotSet"] = NOT_SET,
        match: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if end != NOT_SET:
            kwargs["end"] = end
        if match != NOT_SET:
            kwargs["match"] = match
        super().__init__(**kwargs)


class SpanNotQuery(QueryBase):
    """
    :arg dist: The number of tokens from within the include span that
        can’t have overlap with the exclude span. Equivalent to setting
        both `pre` and `post`.
    :arg exclude: (required)Span query whose matches must not overlap
        those returned.
    :arg include: (required)Span query whose matches are filtered.
    :arg post: The number of tokens after the include span that can’t have
        overlap with the exclude span.
    :arg pre: The number of tokens before the include span that can’t have
        overlap with the exclude span.
    """

    def __init__(
        self,
        *,
        dist: Union[int, "NotSet"] = NOT_SET,
        exclude: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        include: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        post: Union[int, "NotSet"] = NOT_SET,
        pre: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if dist != NOT_SET:
            kwargs["dist"] = dist
        if exclude != NOT_SET:
            kwargs["exclude"] = exclude
        if include != NOT_SET:
            kwargs["include"] = include
        if post != NOT_SET:
            kwargs["post"] = post
        if pre != NOT_SET:
            kwargs["pre"] = pre
        super().__init__(**kwargs)


class SpanWithinQuery(QueryBase):
    """
    :arg big: (required)Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    :arg little: (required)Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    """

    def __init__(
        self,
        *,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if big != NOT_SET:
            kwargs["big"] = big
        if little != NOT_SET:
            kwargs["little"] = little
        super().__init__(**kwargs)


class SpanOrQuery(QueryBase):
    """
    :arg clauses: (required)Array of one or more other span type queries.
    """

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if clauses != NOT_SET:
            kwargs["clauses"] = clauses
        super().__init__(**kwargs)


class HighlightField(HighlightBase):
    """
    :arg fragment_offset: No documentation available.
    :arg matched_fields: No documentation available.
    :arg analyzer: No documentation available.
    """

    def __init__(
        self,
        *,
        fragment_offset: Union[int, "NotSet"] = NOT_SET,
        matched_fields: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        analyzer: Union[
            "a.CustomAnalyzer",
            "a.FingerprintAnalyzer",
            "a.KeywordAnalyzer",
            "a.LanguageAnalyzer",
            "a.NoriAnalyzer",
            "a.PatternAnalyzer",
            "a.SimpleAnalyzer",
            "a.StandardAnalyzer",
            "a.StopAnalyzer",
            "a.WhitespaceAnalyzer",
            "a.IcuAnalyzer",
            "a.KuromojiAnalyzer",
            "a.SnowballAnalyzer",
            "a.DutchAnalyzer",
            "NotSet",
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if fragment_offset != NOT_SET:
            kwargs["fragment_offset"] = fragment_offset
        if matched_fields != NOT_SET:
            kwargs["matched_fields"] = str(matched_fields)
        if analyzer != NOT_SET:
            kwargs["analyzer"] = analyzer
        super().__init__(**kwargs)


class ScriptSort(AttrDict[Any]):
    """
    :arg order: No documentation available.
    :arg script: (required)No documentation available.
    :arg type: No documentation available.
    :arg mode: No documentation available.
    :arg nested: No documentation available.
    """

    def __init__(
        self,
        *,
        order: Union[Literal["asc", "desc"], "NotSet"] = NOT_SET,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        type: Union[Literal["string", "number", "version"], "NotSet"] = NOT_SET,
        mode: Union[Literal["min", "max", "sum", "avg", "median"], "NotSet"] = NOT_SET,
        nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if order != NOT_SET:
            kwargs["order"] = order
        if script != NOT_SET:
            kwargs["script"] = script
        if type != NOT_SET:
            kwargs["type"] = type
        if mode != NOT_SET:
            kwargs["mode"] = mode
        if nested != NOT_SET:
            kwargs["nested"] = nested
        super().__init__(kwargs)


class GeoDistanceSort(AttrDict[Any]):
    """
    :arg mode: No documentation available.
    :arg distance_type: No documentation available.
    :arg ignore_unmapped: No documentation available.
    :arg order: No documentation available.
    :arg unit: No documentation available.
    :arg nested: No documentation available.
    """

    def __init__(
        self,
        *,
        mode: Union[Literal["min", "max", "sum", "avg", "median"], "NotSet"] = NOT_SET,
        distance_type: Union[Literal["arc", "plane"], "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        order: Union[Literal["asc", "desc"], "NotSet"] = NOT_SET,
        unit: Union[
            Literal["in", "ft", "yd", "mi", "nmi", "km", "m", "cm", "mm"], "NotSet"
        ] = NOT_SET,
        nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if mode != NOT_SET:
            kwargs["mode"] = mode
        if distance_type != NOT_SET:
            kwargs["distance_type"] = distance_type
        if ignore_unmapped != NOT_SET:
            kwargs["ignore_unmapped"] = ignore_unmapped
        if order != NOT_SET:
            kwargs["order"] = order
        if unit != NOT_SET:
            kwargs["unit"] = unit
        if nested != NOT_SET:
            kwargs["nested"] = nested
        super().__init__(kwargs)


class ScoreSort(AttrDict[Any]):
    """
    :arg order: No documentation available.
    """

    def __init__(
        self, *, order: Union[Literal["asc", "desc"], "NotSet"] = NOT_SET, **kwargs: Any
    ):
        if order != NOT_SET:
            kwargs["order"] = order
        super().__init__(kwargs)


class IntervalsContainer(AttrDict[Any]):
    """
    :arg all_of: Returns matches that span a combination of other rules.
    :arg any_of: Returns intervals produced by any of its sub-rules.
    :arg fuzzy: Matches analyzed text.
    :arg match: Matches analyzed text.
    :arg prefix: Matches terms that start with a specified set of
        characters.
    :arg wildcard: Matches terms using a wildcard pattern.
    """

    def __init__(
        self,
        *,
        all_of: Union["i.IntervalsAllOf", Dict[str, Any], "NotSet"] = NOT_SET,
        any_of: Union["i.IntervalsAnyOf", Dict[str, Any], "NotSet"] = NOT_SET,
        fuzzy: Union["i.IntervalsFuzzy", Dict[str, Any], "NotSet"] = NOT_SET,
        match: Union["i.IntervalsMatch", Dict[str, Any], "NotSet"] = NOT_SET,
        prefix: Union["i.IntervalsPrefix", Dict[str, Any], "NotSet"] = NOT_SET,
        wildcard: Union["i.IntervalsWildcard", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if all_of != NOT_SET:
            kwargs["all_of"] = all_of
        if any_of != NOT_SET:
            kwargs["any_of"] = any_of
        if fuzzy != NOT_SET:
            kwargs["fuzzy"] = fuzzy
        if match != NOT_SET:
            kwargs["match"] = match
        if prefix != NOT_SET:
            kwargs["prefix"] = prefix
        if wildcard != NOT_SET:
            kwargs["wildcard"] = wildcard
        super().__init__(kwargs)


class IntervalsFilter(AttrDict[Any]):
    """
    :arg after: Query used to return intervals that follow an interval
        from the `filter` rule.
    :arg before: Query used to return intervals that occur before an
        interval from the `filter` rule.
    :arg contained_by: Query used to return intervals contained by an
        interval from the `filter` rule.
    :arg containing: Query used to return intervals that contain an
        interval from the `filter` rule.
    :arg not_contained_by: Query used to return intervals that are **not**
        contained by an interval from the `filter` rule.
    :arg not_containing: Query used to return intervals that do **not**
        contain an interval from the `filter` rule.
    :arg not_overlapping: Query used to return intervals that do **not**
        overlap with an interval from the `filter` rule.
    :arg overlapping: Query used to return intervals that overlap with an
        interval from the `filter` rule.
    :arg script: Script used to return matching documents. This script
        must return a boolean value: `true` or `false`.
    """

    def __init__(
        self,
        *,
        after: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"] = NOT_SET,
        before: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"] = NOT_SET,
        contained_by: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"] = NOT_SET,
        containing: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"] = NOT_SET,
        not_contained_by: Union[
            "i.IntervalsContainer", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        not_containing: Union[
            "i.IntervalsContainer", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        not_overlapping: Union[
            "i.IntervalsContainer", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        overlapping: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"] = NOT_SET,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if after != NOT_SET:
            kwargs["after"] = after
        if before != NOT_SET:
            kwargs["before"] = before
        if contained_by != NOT_SET:
            kwargs["contained_by"] = contained_by
        if containing != NOT_SET:
            kwargs["containing"] = containing
        if not_contained_by != NOT_SET:
            kwargs["not_contained_by"] = not_contained_by
        if not_containing != NOT_SET:
            kwargs["not_containing"] = not_containing
        if not_overlapping != NOT_SET:
            kwargs["not_overlapping"] = not_overlapping
        if overlapping != NOT_SET:
            kwargs["overlapping"] = overlapping
        if script != NOT_SET:
            kwargs["script"] = script
        super().__init__(kwargs)


class NestedSortValue(AttrDict[Any]):
    """
    :arg filter: No documentation available.
    :arg max_children: No documentation available.
    :arg nested: No documentation available.
    :arg path: (required)No documentation available.
    """

    def __init__(
        self,
        *,
        filter: Union[Query, "NotSet"] = NOT_SET,
        max_children: Union[int, "NotSet"] = NOT_SET,
        nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"] = NOT_SET,
        path: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if filter != NOT_SET:
            kwargs["filter"] = filter
        if max_children != NOT_SET:
            kwargs["max_children"] = max_children
        if nested != NOT_SET:
            kwargs["nested"] = nested
        if path != NOT_SET:
            kwargs["path"] = str(path)
        super().__init__(kwargs)
