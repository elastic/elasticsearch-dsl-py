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

    boost: Union[float, "NotSet"]
    _name: Union[str, "NotSet"]

    def __init__(
        self,
        *,
        boost: Union[float, "NotSet"] = NOT_SET,
        _name: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(boost, NotSet):
            kwargs["boost"] = boost
        if not isinstance(_name, NotSet):
            kwargs["_name"] = _name
        super().__init__(kwargs)


class CommonTermsQuery(QueryBase):
    """
    :arg analyzer: No documentation available.
    :arg cutoff_frequency: No documentation available.
    :arg high_freq_operator: No documentation available.
    :arg low_freq_operator: No documentation available.
    :arg minimum_should_match: No documentation available.
    :arg query: (required) No documentation available.
    """

    analyzer: Union[str, "NotSet"]
    cutoff_frequency: Union[float, "NotSet"]
    high_freq_operator: Union[Literal["and", "or"], "NotSet"]
    low_freq_operator: Union[Literal["and", "or"], "NotSet"]
    minimum_should_match: Union[int, str, "NotSet"]
    query: Union[str, "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(cutoff_frequency, NotSet):
            kwargs["cutoff_frequency"] = cutoff_frequency
        if not isinstance(high_freq_operator, NotSet):
            kwargs["high_freq_operator"] = high_freq_operator
        if not isinstance(low_freq_operator, NotSet):
            kwargs["low_freq_operator"] = low_freq_operator
        if not isinstance(minimum_should_match, NotSet):
            kwargs["minimum_should_match"] = minimum_should_match
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        super().__init__(**kwargs)


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

    exp: Union["f.DecayFunction", "NotSet"]
    gauss: Union["f.DecayFunction", "NotSet"]
    linear: Union["f.DecayFunction", "NotSet"]
    field_value_factor: Union["f.FieldValueFactor", "NotSet"]
    random_score: Union["f.RandomScore", "NotSet"]
    script_score: Union["f.ScriptScore", "NotSet"]
    filter: Union[Query, "NotSet"]
    weight: Union[float, "NotSet"]

    def __init__(
        self,
        *,
        exp: Union["f.DecayFunction", "NotSet"] = NOT_SET,
        gauss: Union["f.DecayFunction", "NotSet"] = NOT_SET,
        linear: Union["f.DecayFunction", "NotSet"] = NOT_SET,
        field_value_factor: Union["f.FieldValueFactor", "NotSet"] = NOT_SET,
        random_score: Union["f.RandomScore", "NotSet"] = NOT_SET,
        script_score: Union["f.ScriptScore", "NotSet"] = NOT_SET,
        filter: Union[Query, "NotSet"] = NOT_SET,
        weight: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(exp, NotSet):
            kwargs["exp"] = exp
        if not isinstance(gauss, NotSet):
            kwargs["gauss"] = gauss
        if not isinstance(linear, NotSet):
            kwargs["linear"] = linear
        if not isinstance(field_value_factor, NotSet):
            kwargs["field_value_factor"] = field_value_factor
        if not isinstance(random_score, NotSet):
            kwargs["random_score"] = random_score
        if not isinstance(script_score, NotSet):
            kwargs["script_score"] = script_score
        if not isinstance(filter, NotSet):
            kwargs["filter"] = filter
        if not isinstance(weight, NotSet):
            kwargs["weight"] = weight
        super().__init__(kwargs)


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
    :arg value: (required) Term you wish to find in the provided field.
    """

    max_expansions: Union[int, "NotSet"]
    prefix_length: Union[int, "NotSet"]
    rewrite: Union[str, "NotSet"]
    transpositions: Union[bool, "NotSet"]
    fuzziness: Union[str, int, "NotSet"]
    value: Union[str, float, bool, "NotSet"]

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
        if not isinstance(max_expansions, NotSet):
            kwargs["max_expansions"] = max_expansions
        if not isinstance(prefix_length, NotSet):
            kwargs["prefix_length"] = prefix_length
        if not isinstance(rewrite, NotSet):
            kwargs["rewrite"] = rewrite
        if not isinstance(transpositions, NotSet):
            kwargs["transpositions"] = transpositions
        if not isinstance(fuzziness, NotSet):
            kwargs["fuzziness"] = fuzziness
        if not isinstance(value, NotSet):
            kwargs["value"] = value
        super().__init__(**kwargs)


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

    name: Union[str, "NotSet"]
    size: Union[int, "NotSet"]
    from_: Union[int, "NotSet"]
    collapse: Union["i.FieldCollapse", Dict[str, Any], "NotSet"]
    docvalue_fields: Union[List["i.FieldAndFormat"], Dict[str, Any], "NotSet"]
    explain: Union[bool, "NotSet"]
    highlight: Union["i.Highlight", Dict[str, Any], "NotSet"]
    ignore_unmapped: Union[bool, "NotSet"]
    script_fields: Union[
        Mapping[Union[str, "InstrumentedField"], "i.ScriptField"],
        Dict[str, Any],
        "NotSet",
    ]
    seq_no_primary_term: Union[bool, "NotSet"]
    fields: Union[
        Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]], "NotSet"
    ]
    sort: Union[
        Union[Union[str, "InstrumentedField"], "i.SortOptions"],
        List[Union[Union[str, "InstrumentedField"], "i.SortOptions"]],
        Dict[str, Any],
        "NotSet",
    ]
    _source: Union[bool, "i.SourceFilter", Dict[str, Any], "NotSet"]
    stored_fields: Union[
        Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]], "NotSet"
    ]
    track_scores: Union[bool, "NotSet"]
    version: Union[bool, "NotSet"]

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
        if not isinstance(name, NotSet):
            kwargs["name"] = name
        if not isinstance(size, NotSet):
            kwargs["size"] = size
        if not isinstance(from_, NotSet):
            kwargs["from_"] = from_
        if not isinstance(collapse, NotSet):
            kwargs["collapse"] = collapse
        if not isinstance(docvalue_fields, NotSet):
            kwargs["docvalue_fields"] = docvalue_fields
        if not isinstance(explain, NotSet):
            kwargs["explain"] = explain
        if not isinstance(highlight, NotSet):
            kwargs["highlight"] = highlight
        if not isinstance(ignore_unmapped, NotSet):
            kwargs["ignore_unmapped"] = ignore_unmapped
        if not isinstance(script_fields, NotSet):
            kwargs["script_fields"] = str(script_fields)
        if not isinstance(seq_no_primary_term, NotSet):
            kwargs["seq_no_primary_term"] = seq_no_primary_term
        if not isinstance(fields, NotSet):
            kwargs["fields"] = str(fields)
        if not isinstance(sort, NotSet):
            kwargs["sort"] = str(sort)
        if not isinstance(_source, NotSet):
            kwargs["_source"] = _source
        if not isinstance(stored_fields, NotSet):
            kwargs["stored_fields"] = str(stored_fields)
        if not isinstance(track_scores, NotSet):
            kwargs["track_scores"] = track_scores
        if not isinstance(version, NotSet):
            kwargs["version"] = version
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

    all_of: Union["i.IntervalsAllOf", Dict[str, Any], "NotSet"]
    any_of: Union["i.IntervalsAnyOf", Dict[str, Any], "NotSet"]
    fuzzy: Union["i.IntervalsFuzzy", Dict[str, Any], "NotSet"]
    match: Union["i.IntervalsMatch", Dict[str, Any], "NotSet"]
    prefix: Union["i.IntervalsPrefix", Dict[str, Any], "NotSet"]
    wildcard: Union["i.IntervalsWildcard", Dict[str, Any], "NotSet"]

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
        if not isinstance(all_of, NotSet):
            kwargs["all_of"] = all_of
        if not isinstance(any_of, NotSet):
            kwargs["any_of"] = any_of
        if not isinstance(fuzzy, NotSet):
            kwargs["fuzzy"] = fuzzy
        if not isinstance(match, NotSet):
            kwargs["match"] = match
        if not isinstance(prefix, NotSet):
            kwargs["prefix"] = prefix
        if not isinstance(wildcard, NotSet):
            kwargs["wildcard"] = wildcard
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

    doc: Any
    fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"]
    _id: Union[str, "NotSet"]
    _index: Union[str, "NotSet"]
    per_field_analyzer: Union[Mapping[Union[str, "InstrumentedField"], str], "NotSet"]
    routing: Union[str, "NotSet"]
    version: Union[int, "NotSet"]
    version_type: Union[
        Literal["internal", "external", "external_gte", "force"], "NotSet"
    ]

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
        if not isinstance(doc, NotSet):
            kwargs["doc"] = doc
        if not isinstance(fields, NotSet):
            kwargs["fields"] = str(fields)
        if not isinstance(_id, NotSet):
            kwargs["_id"] = _id
        if not isinstance(_index, NotSet):
            kwargs["_index"] = _index
        if not isinstance(per_field_analyzer, NotSet):
            kwargs["per_field_analyzer"] = str(per_field_analyzer)
        if not isinstance(routing, NotSet):
            kwargs["routing"] = routing
        if not isinstance(version, NotSet):
            kwargs["version"] = version
        if not isinstance(version_type, NotSet):
            kwargs["version_type"] = version_type
        super().__init__(kwargs)


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
    :arg query: (required) Terms you wish to find in the provided field.
        The last term is used in a prefix query.
    """

    analyzer: Union[str, "NotSet"]
    fuzziness: Union[str, int, "NotSet"]
    fuzzy_rewrite: Union[str, "NotSet"]
    fuzzy_transpositions: Union[bool, "NotSet"]
    max_expansions: Union[int, "NotSet"]
    minimum_should_match: Union[int, str, "NotSet"]
    operator: Union[Literal["and", "or"], "NotSet"]
    prefix_length: Union[int, "NotSet"]
    query: Union[str, "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(fuzziness, NotSet):
            kwargs["fuzziness"] = fuzziness
        if not isinstance(fuzzy_rewrite, NotSet):
            kwargs["fuzzy_rewrite"] = fuzzy_rewrite
        if not isinstance(fuzzy_transpositions, NotSet):
            kwargs["fuzzy_transpositions"] = fuzzy_transpositions
        if not isinstance(max_expansions, NotSet):
            kwargs["max_expansions"] = max_expansions
        if not isinstance(minimum_should_match, NotSet):
            kwargs["minimum_should_match"] = minimum_should_match
        if not isinstance(operator, NotSet):
            kwargs["operator"] = operator
        if not isinstance(prefix_length, NotSet):
            kwargs["prefix_length"] = prefix_length
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        super().__init__(**kwargs)


class MatchPhrasePrefixQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert text in the query value into
        tokens.
    :arg max_expansions: Maximum number of terms to which the last
        provided term of the query value will expand.
    :arg query: (required) Text you wish to find in the provided field.
    :arg slop: Maximum number of positions allowed between matching
        tokens.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the analyzer removes all tokens, such as when using a `stop`
        filter.
    """

    analyzer: Union[str, "NotSet"]
    max_expansions: Union[int, "NotSet"]
    query: Union[str, "NotSet"]
    slop: Union[int, "NotSet"]
    zero_terms_query: Union[Literal["all", "none"], "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(max_expansions, NotSet):
            kwargs["max_expansions"] = max_expansions
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        if not isinstance(slop, NotSet):
            kwargs["slop"] = slop
        if not isinstance(zero_terms_query, NotSet):
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


class MatchPhraseQuery(QueryBase):
    """
    :arg analyzer: Analyzer used to convert the text in the query value
        into tokens.
    :arg query: (required) Query terms that are analyzed and turned into a
        phrase query.
    :arg slop: Maximum number of positions allowed between matching
        tokens.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the `analyzer` removes all tokens, such as when using a `stop`
        filter.
    """

    analyzer: Union[str, "NotSet"]
    query: Union[str, "NotSet"]
    slop: Union[int, "NotSet"]
    zero_terms_query: Union[Literal["all", "none"], "NotSet"]

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        zero_terms_query: Union[Literal["all", "none"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        if not isinstance(slop, NotSet):
            kwargs["slop"] = slop
        if not isinstance(zero_terms_query, NotSet):
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


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
    :arg query: (required) Text, number, boolean value or date you wish to
        find in the provided field.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the `analyzer` removes all tokens, such as when using a `stop`
        filter.
    """

    analyzer: Union[str, "NotSet"]
    auto_generate_synonyms_phrase_query: Union[bool, "NotSet"]
    cutoff_frequency: Union[float, "NotSet"]
    fuzziness: Union[str, int, "NotSet"]
    fuzzy_rewrite: Union[str, "NotSet"]
    fuzzy_transpositions: Union[bool, "NotSet"]
    lenient: Union[bool, "NotSet"]
    max_expansions: Union[int, "NotSet"]
    minimum_should_match: Union[int, str, "NotSet"]
    operator: Union[Literal["and", "or"], "NotSet"]
    prefix_length: Union[int, "NotSet"]
    query: Union[str, float, bool, "NotSet"]
    zero_terms_query: Union[Literal["all", "none"], "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(auto_generate_synonyms_phrase_query, NotSet):
            kwargs["auto_generate_synonyms_phrase_query"] = (
                auto_generate_synonyms_phrase_query
            )
        if not isinstance(cutoff_frequency, NotSet):
            kwargs["cutoff_frequency"] = cutoff_frequency
        if not isinstance(fuzziness, NotSet):
            kwargs["fuzziness"] = fuzziness
        if not isinstance(fuzzy_rewrite, NotSet):
            kwargs["fuzzy_rewrite"] = fuzzy_rewrite
        if not isinstance(fuzzy_transpositions, NotSet):
            kwargs["fuzzy_transpositions"] = fuzzy_transpositions
        if not isinstance(lenient, NotSet):
            kwargs["lenient"] = lenient
        if not isinstance(max_expansions, NotSet):
            kwargs["max_expansions"] = max_expansions
        if not isinstance(minimum_should_match, NotSet):
            kwargs["minimum_should_match"] = minimum_should_match
        if not isinstance(operator, NotSet):
            kwargs["operator"] = operator
        if not isinstance(prefix_length, NotSet):
            kwargs["prefix_length"] = prefix_length
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        if not isinstance(zero_terms_query, NotSet):
            kwargs["zero_terms_query"] = zero_terms_query
        super().__init__(**kwargs)


class PinnedDoc(AttrDict[Any]):
    """
    :arg _id: (required) The unique document ID.
    :arg _index: (required) The index that contains the document.
    """

    _id: Union[str, "NotSet"]
    _index: Union[str, "NotSet"]

    def __init__(
        self,
        *,
        _id: Union[str, "NotSet"] = NOT_SET,
        _index: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_id, NotSet):
            kwargs["_id"] = _id
        if not isinstance(_index, NotSet):
            kwargs["_index"] = _index
        super().__init__(kwargs)


class PrefixQuery(QueryBase):
    """
    :arg rewrite: Method used to rewrite the query.
    :arg value: (required) Beginning characters of terms you wish to find
        in the provided field.
    :arg case_insensitive: Allows ASCII case insensitive matching of the
        value with the indexed field values when set to `true`. Default is
        `false` which means the case sensitivity of matching depends on
        the underlying field’s mapping.
    """

    rewrite: Union[str, "NotSet"]
    value: Union[str, "NotSet"]
    case_insensitive: Union[bool, "NotSet"]

    def __init__(
        self,
        *,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        value: Union[str, "NotSet"] = NOT_SET,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(rewrite, NotSet):
            kwargs["rewrite"] = rewrite
        if not isinstance(value, NotSet):
            kwargs["value"] = value
        if not isinstance(case_insensitive, NotSet):
            kwargs["case_insensitive"] = case_insensitive
        super().__init__(**kwargs)


class QueryVectorBuilder(AttrDict[Any]):
    """
    :arg text_embedding: No documentation available.
    """

    text_embedding: Union["i.TextEmbedding", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        text_embedding: Union["i.TextEmbedding", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(text_embedding, NotSet):
            kwargs["text_embedding"] = text_embedding
        super().__init__(kwargs)


class RankFeatureFunction(AttrDict[Any]):
    pass


class RankFeatureFunctionLinear(RankFeatureFunction):
    pass


class RankFeatureFunctionLogarithm(RankFeatureFunction):
    """
    :arg scaling_factor: (required) Configurable scaling factor.
    """

    scaling_factor: Union[float, "NotSet"]

    def __init__(
        self, *, scaling_factor: Union[float, "NotSet"] = NOT_SET, **kwargs: Any
    ):
        if not isinstance(scaling_factor, NotSet):
            kwargs["scaling_factor"] = scaling_factor
        super().__init__(**kwargs)


class RankFeatureFunctionSaturation(RankFeatureFunction):
    """
    :arg pivot: Configurable pivot value so that the result will be less
        than 0.5.
    """

    pivot: Union[float, "NotSet"]

    def __init__(self, *, pivot: Union[float, "NotSet"] = NOT_SET, **kwargs: Any):
        if not isinstance(pivot, NotSet):
            kwargs["pivot"] = pivot
        super().__init__(**kwargs)


class RankFeatureFunctionSigmoid(RankFeatureFunction):
    """
    :arg pivot: (required) Configurable pivot value so that the result
        will be less than 0.5.
    :arg exponent: (required) Configurable Exponent.
    """

    pivot: Union[float, "NotSet"]
    exponent: Union[float, "NotSet"]

    def __init__(
        self,
        *,
        pivot: Union[float, "NotSet"] = NOT_SET,
        exponent: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(pivot, NotSet):
            kwargs["pivot"] = pivot
        if not isinstance(exponent, NotSet):
            kwargs["exponent"] = exponent
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
    :arg value: (required) Regular expression for terms you wish to find
        in the provided field.
    """

    case_insensitive: Union[bool, "NotSet"]
    flags: Union[str, "NotSet"]
    max_determinized_states: Union[int, "NotSet"]
    rewrite: Union[str, "NotSet"]
    value: Union[str, "NotSet"]

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
        if not isinstance(case_insensitive, NotSet):
            kwargs["case_insensitive"] = case_insensitive
        if not isinstance(flags, NotSet):
            kwargs["flags"] = flags
        if not isinstance(max_determinized_states, NotSet):
            kwargs["max_determinized_states"] = max_determinized_states
        if not isinstance(rewrite, NotSet):
            kwargs["rewrite"] = rewrite
        if not isinstance(value, NotSet):
            kwargs["value"] = value
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

    source: Union[str, "NotSet"]
    id: Union[str, "NotSet"]
    params: Union[Mapping[str, Any], "NotSet"]
    lang: Union[Literal["painless", "expression", "mustache", "java"], "NotSet"]
    options: Union[Mapping[str, str], "NotSet"]

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
        if not isinstance(source, NotSet):
            kwargs["source"] = source
        if not isinstance(id, NotSet):
            kwargs["id"] = id
        if not isinstance(params, NotSet):
            kwargs["params"] = params
        if not isinstance(lang, NotSet):
            kwargs["lang"] = lang
        if not isinstance(options, NotSet):
            kwargs["options"] = options
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

    span_containing: Union["i.SpanContainingQuery", Dict[str, Any], "NotSet"]
    span_field_masking: Union["i.SpanFieldMaskingQuery", Dict[str, Any], "NotSet"]
    span_first: Union["i.SpanFirstQuery", Dict[str, Any], "NotSet"]
    span_gap: Union[Mapping[Union[str, "InstrumentedField"], int], "NotSet"]
    span_multi: Union["i.SpanMultiTermQuery", Dict[str, Any], "NotSet"]
    span_near: Union["i.SpanNearQuery", Dict[str, Any], "NotSet"]
    span_not: Union["i.SpanNotQuery", Dict[str, Any], "NotSet"]
    span_or: Union["i.SpanOrQuery", Dict[str, Any], "NotSet"]
    span_term: Union[
        Mapping[Union[str, "InstrumentedField"], "i.SpanTermQuery"],
        Dict[str, Any],
        "NotSet",
    ]
    span_within: Union["i.SpanWithinQuery", Dict[str, Any], "NotSet"]

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
        if not isinstance(span_containing, NotSet):
            kwargs["span_containing"] = span_containing
        if not isinstance(span_field_masking, NotSet):
            kwargs["span_field_masking"] = span_field_masking
        if not isinstance(span_first, NotSet):
            kwargs["span_first"] = span_first
        if not isinstance(span_gap, NotSet):
            kwargs["span_gap"] = str(span_gap)
        if not isinstance(span_multi, NotSet):
            kwargs["span_multi"] = span_multi
        if not isinstance(span_near, NotSet):
            kwargs["span_near"] = span_near
        if not isinstance(span_not, NotSet):
            kwargs["span_not"] = span_not
        if not isinstance(span_or, NotSet):
            kwargs["span_or"] = span_or
        if not isinstance(span_term, NotSet):
            kwargs["span_term"] = str(span_term)
        if not isinstance(span_within, NotSet):
            kwargs["span_within"] = span_within
        super().__init__(kwargs)


class SpanTermQuery(QueryBase):
    """
    :arg value: (required) No documentation available.
    """

    value: Union[str, "NotSet"]

    def __init__(self, *, value: Union[str, "NotSet"] = NOT_SET, **kwargs: Any):
        if not isinstance(value, NotSet):
            kwargs["value"] = value
        super().__init__(**kwargs)


class TermQuery(QueryBase):
    """
    :arg value: (required) Term you wish to find in the provided field.
    :arg case_insensitive: Allows ASCII case insensitive matching of the
        value with the indexed field values when set to `true`. When
        `false`, the case sensitivity of matching depends on the
        underlying field’s mapping.
    """

    value: Union[int, float, str, bool, None, Any, "NotSet"]
    case_insensitive: Union[bool, "NotSet"]

    def __init__(
        self,
        *,
        value: Union[int, float, str, bool, None, Any, "NotSet"] = NOT_SET,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(value, NotSet):
            kwargs["value"] = value
        if not isinstance(case_insensitive, NotSet):
            kwargs["case_insensitive"] = case_insensitive
        super().__init__(**kwargs)


class TermsSetQuery(QueryBase):
    """
    :arg minimum_should_match_field: Numeric field containing the number
        of matching terms required to return a document.
    :arg minimum_should_match_script: Custom script containing the number
        of matching terms required to return a document.
    :arg terms: (required) Array of terms you wish to find in the provided
        field.
    """

    minimum_should_match_field: Union[str, "InstrumentedField", "NotSet"]
    minimum_should_match_script: Union["i.Script", Dict[str, Any], "NotSet"]
    terms: Union[List[str], "NotSet"]

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
        if not isinstance(minimum_should_match_field, NotSet):
            kwargs["minimum_should_match_field"] = str(minimum_should_match_field)
        if not isinstance(minimum_should_match_script, NotSet):
            kwargs["minimum_should_match_script"] = minimum_should_match_script
        if not isinstance(terms, NotSet):
            kwargs["terms"] = terms
        super().__init__(**kwargs)


class TextExpansionQuery(QueryBase):
    """
    :arg model_id: (required) The text expansion NLP model to use
    :arg model_text: (required) The query text
    :arg pruning_config: Token pruning configurations
    """

    model_id: Union[str, "NotSet"]
    model_text: Union[str, "NotSet"]
    pruning_config: Union["i.TokenPruningConfig", Dict[str, Any], "NotSet"]

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
        if not isinstance(model_id, NotSet):
            kwargs["model_id"] = model_id
        if not isinstance(model_text, NotSet):
            kwargs["model_text"] = model_text
        if not isinstance(pruning_config, NotSet):
            kwargs["pruning_config"] = pruning_config
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

    tokens_freq_ratio_threshold: Union[int, "NotSet"]
    tokens_weight_threshold: Union[float, "NotSet"]
    only_score_pruned_tokens: Union[bool, "NotSet"]

    def __init__(
        self,
        *,
        tokens_freq_ratio_threshold: Union[int, "NotSet"] = NOT_SET,
        tokens_weight_threshold: Union[float, "NotSet"] = NOT_SET,
        only_score_pruned_tokens: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(tokens_freq_ratio_threshold, NotSet):
            kwargs["tokens_freq_ratio_threshold"] = tokens_freq_ratio_threshold
        if not isinstance(tokens_weight_threshold, NotSet):
            kwargs["tokens_weight_threshold"] = tokens_weight_threshold
        if not isinstance(only_score_pruned_tokens, NotSet):
            kwargs["only_score_pruned_tokens"] = only_score_pruned_tokens
        super().__init__(kwargs)


class WeightedTokensQuery(QueryBase):
    """
    :arg tokens: (required) The tokens representing this query
    :arg pruning_config: Token pruning configurations
    """

    tokens: Union[Mapping[str, float], "NotSet"]
    pruning_config: Union["i.TokenPruningConfig", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        tokens: Union[Mapping[str, float], "NotSet"] = NOT_SET,
        pruning_config: Union[
            "i.TokenPruningConfig", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(tokens, NotSet):
            kwargs["tokens"] = tokens
        if not isinstance(pruning_config, NotSet):
            kwargs["pruning_config"] = pruning_config
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

    case_insensitive: Union[bool, "NotSet"]
    rewrite: Union[str, "NotSet"]
    value: Union[str, "NotSet"]
    wildcard: Union[str, "NotSet"]

    def __init__(
        self,
        *,
        case_insensitive: Union[bool, "NotSet"] = NOT_SET,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        value: Union[str, "NotSet"] = NOT_SET,
        wildcard: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(case_insensitive, NotSet):
            kwargs["case_insensitive"] = case_insensitive
        if not isinstance(rewrite, NotSet):
            kwargs["rewrite"] = rewrite
        if not isinstance(value, NotSet):
            kwargs["value"] = value
        if not isinstance(wildcard, NotSet):
            kwargs["wildcard"] = wildcard
        super().__init__(**kwargs)


class FieldAndFormat(AttrDict[Any]):
    """
    :arg field: (required) Wildcard pattern. The request returns values
        for field names matching this pattern.
    :arg format: Format in which the values are returned.
    :arg include_unmapped: No documentation available.
    """

    field: Union[str, "InstrumentedField", "NotSet"]
    format: Union[str, "NotSet"]
    include_unmapped: Union[bool, "NotSet"]

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        format: Union[str, "NotSet"] = NOT_SET,
        include_unmapped: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(field, NotSet):
            kwargs["field"] = str(field)
        if not isinstance(format, NotSet):
            kwargs["format"] = format
        if not isinstance(include_unmapped, NotSet):
            kwargs["include_unmapped"] = include_unmapped
        super().__init__(kwargs)


class FieldCollapse(AttrDict[Any]):
    """
    :arg field: (required) The field to collapse the result set on
    :arg inner_hits: The number of inner hits and their sort order
    :arg max_concurrent_group_searches: The number of concurrent requests
        allowed to retrieve the inner_hits per group
    :arg collapse: No documentation available.
    """

    field: Union[str, "InstrumentedField", "NotSet"]
    inner_hits: Union["i.InnerHits", List["i.InnerHits"], Dict[str, Any], "NotSet"]
    max_concurrent_group_searches: Union[int, "NotSet"]
    collapse: Union["i.FieldCollapse", Dict[str, Any], "NotSet"]

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
        if not isinstance(field, NotSet):
            kwargs["field"] = str(field)
        if not isinstance(inner_hits, NotSet):
            kwargs["inner_hits"] = inner_hits
        if not isinstance(max_concurrent_group_searches, NotSet):
            kwargs["max_concurrent_group_searches"] = max_concurrent_group_searches
        if not isinstance(collapse, NotSet):
            kwargs["collapse"] = collapse
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

    type: Union[Literal["plain", "fvh", "unified"], "NotSet"]
    boundary_chars: Union[str, "NotSet"]
    boundary_max_scan: Union[int, "NotSet"]
    boundary_scanner: Union[Literal["chars", "sentence", "word"], "NotSet"]
    boundary_scanner_locale: Union[str, "NotSet"]
    force_source: Union[bool, "NotSet"]
    fragmenter: Union[Literal["simple", "span"], "NotSet"]
    fragment_size: Union[int, "NotSet"]
    highlight_filter: Union[bool, "NotSet"]
    highlight_query: Union[Query, "NotSet"]
    max_fragment_length: Union[int, "NotSet"]
    max_analyzed_offset: Union[int, "NotSet"]
    no_match_size: Union[int, "NotSet"]
    number_of_fragments: Union[int, "NotSet"]
    options: Union[Mapping[str, Any], "NotSet"]
    order: Union[Literal["score"], "NotSet"]
    phrase_limit: Union[int, "NotSet"]
    post_tags: Union[List[str], "NotSet"]
    pre_tags: Union[List[str], "NotSet"]
    require_field_match: Union[bool, "NotSet"]
    tags_schema: Union[Literal["styled"], "NotSet"]

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
        if not isinstance(type, NotSet):
            kwargs["type"] = type
        if not isinstance(boundary_chars, NotSet):
            kwargs["boundary_chars"] = boundary_chars
        if not isinstance(boundary_max_scan, NotSet):
            kwargs["boundary_max_scan"] = boundary_max_scan
        if not isinstance(boundary_scanner, NotSet):
            kwargs["boundary_scanner"] = boundary_scanner
        if not isinstance(boundary_scanner_locale, NotSet):
            kwargs["boundary_scanner_locale"] = boundary_scanner_locale
        if not isinstance(force_source, NotSet):
            kwargs["force_source"] = force_source
        if not isinstance(fragmenter, NotSet):
            kwargs["fragmenter"] = fragmenter
        if not isinstance(fragment_size, NotSet):
            kwargs["fragment_size"] = fragment_size
        if not isinstance(highlight_filter, NotSet):
            kwargs["highlight_filter"] = highlight_filter
        if not isinstance(highlight_query, NotSet):
            kwargs["highlight_query"] = highlight_query
        if not isinstance(max_fragment_length, NotSet):
            kwargs["max_fragment_length"] = max_fragment_length
        if not isinstance(max_analyzed_offset, NotSet):
            kwargs["max_analyzed_offset"] = max_analyzed_offset
        if not isinstance(no_match_size, NotSet):
            kwargs["no_match_size"] = no_match_size
        if not isinstance(number_of_fragments, NotSet):
            kwargs["number_of_fragments"] = number_of_fragments
        if not isinstance(options, NotSet):
            kwargs["options"] = options
        if not isinstance(order, NotSet):
            kwargs["order"] = order
        if not isinstance(phrase_limit, NotSet):
            kwargs["phrase_limit"] = phrase_limit
        if not isinstance(post_tags, NotSet):
            kwargs["post_tags"] = post_tags
        if not isinstance(pre_tags, NotSet):
            kwargs["pre_tags"] = pre_tags
        if not isinstance(require_field_match, NotSet):
            kwargs["require_field_match"] = require_field_match
        if not isinstance(tags_schema, NotSet):
            kwargs["tags_schema"] = tags_schema
        super().__init__(kwargs)


class Highlight(HighlightBase):
    """
    :arg encoder: No documentation available.
    :arg fields: (required) No documentation available.
    """

    encoder: Union[Literal["default", "html"], "NotSet"]
    fields: Union[
        Mapping[Union[str, "InstrumentedField"], "i.HighlightField"],
        Dict[str, Any],
        "NotSet",
    ]

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
        if not isinstance(encoder, NotSet):
            kwargs["encoder"] = encoder
        if not isinstance(fields, NotSet):
            kwargs["fields"] = str(fields)
        super().__init__(**kwargs)


class ScriptField(AttrDict[Any]):
    """
    :arg script: (required) No documentation available.
    :arg ignore_failure: No documentation available.
    """

    script: Union["i.Script", Dict[str, Any], "NotSet"]
    ignore_failure: Union[bool, "NotSet"]

    def __init__(
        self,
        *,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        ignore_failure: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(script, NotSet):
            kwargs["script"] = script
        if not isinstance(ignore_failure, NotSet):
            kwargs["ignore_failure"] = ignore_failure
        super().__init__(kwargs)


class SortOptions(AttrDict[Any]):
    """
    :arg _score: No documentation available.
    :arg _doc: No documentation available.
    :arg _geo_distance: No documentation available.
    :arg _script: No documentation available.
    """

    _score: Union["i.ScoreSort", Dict[str, Any], "NotSet"]
    _doc: Union["i.ScoreSort", Dict[str, Any], "NotSet"]
    _geo_distance: Union["i.GeoDistanceSort", Dict[str, Any], "NotSet"]
    _script: Union["i.ScriptSort", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        _score: Union["i.ScoreSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _doc: Union["i.ScoreSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _geo_distance: Union["i.GeoDistanceSort", Dict[str, Any], "NotSet"] = NOT_SET,
        _script: Union["i.ScriptSort", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_score, NotSet):
            kwargs["_score"] = _score
        if not isinstance(_doc, NotSet):
            kwargs["_doc"] = _doc
        if not isinstance(_geo_distance, NotSet):
            kwargs["_geo_distance"] = _geo_distance
        if not isinstance(_script, NotSet):
            kwargs["_script"] = _script
        super().__init__(kwargs)


class SourceFilter(AttrDict[Any]):
    """
    :arg excludes: No documentation available.
    :arg includes: No documentation available.
    """

    excludes: Union[
        Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]], "NotSet"
    ]
    includes: Union[
        Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]], "NotSet"
    ]

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
        if not isinstance(excludes, NotSet):
            kwargs["excludes"] = str(excludes)
        if not isinstance(includes, NotSet):
            kwargs["includes"] = str(includes)
        super().__init__(kwargs)


class IntervalsAllOf(AttrDict[Any]):
    """
    :arg intervals: (required) An array of rules to combine. All rules
        must produce a match in a document for the overall source to
        match.
    :arg max_gaps: Maximum number of positions between the matching terms.
        Intervals produced by the rules further apart than this are not
        considered matches.
    :arg ordered: If `true`, intervals produced by the rules should appear
        in the order in which they are specified.
    :arg filter: Rule used to filter returned intervals.
    """

    intervals: Union[List["i.IntervalsContainer"], Dict[str, Any], "NotSet"]
    max_gaps: Union[int, "NotSet"]
    ordered: Union[bool, "NotSet"]
    filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"]

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
        if not isinstance(intervals, NotSet):
            kwargs["intervals"] = intervals
        if not isinstance(max_gaps, NotSet):
            kwargs["max_gaps"] = max_gaps
        if not isinstance(ordered, NotSet):
            kwargs["ordered"] = ordered
        if not isinstance(filter, NotSet):
            kwargs["filter"] = filter
        super().__init__(kwargs)


class IntervalsAnyOf(AttrDict[Any]):
    """
    :arg intervals: (required) An array of rules to match.
    :arg filter: Rule used to filter returned intervals.
    """

    intervals: Union[List["i.IntervalsContainer"], Dict[str, Any], "NotSet"]
    filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        intervals: Union[
            List["i.IntervalsContainer"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(intervals, NotSet):
            kwargs["intervals"] = intervals
        if not isinstance(filter, NotSet):
            kwargs["filter"] = filter
        super().__init__(kwargs)


class IntervalsFuzzy(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to normalize the term.
    :arg fuzziness: Maximum edit distance allowed for matching.
    :arg prefix_length: Number of beginning characters left unchanged when
        creating expansions.
    :arg term: (required) The term to match.
    :arg transpositions: Indicates whether edits include transpositions of
        two adjacent characters (for example, `ab` to `ba`).
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `term` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    analyzer: Union[str, "NotSet"]
    fuzziness: Union[str, int, "NotSet"]
    prefix_length: Union[int, "NotSet"]
    term: Union[str, "NotSet"]
    transpositions: Union[bool, "NotSet"]
    use_field: Union[str, "InstrumentedField", "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(fuzziness, NotSet):
            kwargs["fuzziness"] = fuzziness
        if not isinstance(prefix_length, NotSet):
            kwargs["prefix_length"] = prefix_length
        if not isinstance(term, NotSet):
            kwargs["term"] = term
        if not isinstance(transpositions, NotSet):
            kwargs["transpositions"] = transpositions
        if not isinstance(use_field, NotSet):
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class IntervalsMatch(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze terms in the query.
    :arg max_gaps: Maximum number of positions between the matching terms.
        Terms further apart than this are not considered matches.
    :arg ordered: If `true`, matching terms must appear in their specified
        order.
    :arg query: (required) Text you wish to find in the provided field.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `term` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    :arg filter: An optional interval filter.
    """

    analyzer: Union[str, "NotSet"]
    max_gaps: Union[int, "NotSet"]
    ordered: Union[bool, "NotSet"]
    query: Union[str, "NotSet"]
    use_field: Union[str, "InstrumentedField", "NotSet"]
    filter: Union["i.IntervalsFilter", Dict[str, Any], "NotSet"]

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
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(max_gaps, NotSet):
            kwargs["max_gaps"] = max_gaps
        if not isinstance(ordered, NotSet):
            kwargs["ordered"] = ordered
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        if not isinstance(use_field, NotSet):
            kwargs["use_field"] = str(use_field)
        if not isinstance(filter, NotSet):
            kwargs["filter"] = filter
        super().__init__(kwargs)


class IntervalsPrefix(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze the `prefix`.
    :arg prefix: (required) Beginning characters of terms you wish to find
        in the top-level field.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `prefix` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    analyzer: Union[str, "NotSet"]
    prefix: Union[str, "NotSet"]
    use_field: Union[str, "InstrumentedField", "NotSet"]

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        prefix: Union[str, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(prefix, NotSet):
            kwargs["prefix"] = prefix
        if not isinstance(use_field, NotSet):
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class IntervalsWildcard(AttrDict[Any]):
    """
    :arg analyzer: Analyzer used to analyze the `pattern`. Defaults to the
        top-level field's analyzer.
    :arg pattern: (required) Wildcard pattern used to find matching terms.
    :arg use_field: If specified, match intervals from this field rather
        than the top-level field. The `pattern` is normalized using the
        search analyzer from this field, unless `analyzer` is specified
        separately.
    """

    analyzer: Union[str, "NotSet"]
    pattern: Union[str, "NotSet"]
    use_field: Union[str, "InstrumentedField", "NotSet"]

    def __init__(
        self,
        *,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        pattern: Union[str, "NotSet"] = NOT_SET,
        use_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        if not isinstance(pattern, NotSet):
            kwargs["pattern"] = pattern
        if not isinstance(use_field, NotSet):
            kwargs["use_field"] = str(use_field)
        super().__init__(kwargs)


class TextEmbedding(AttrDict[Any]):
    """
    :arg model_id: (required) No documentation available.
    :arg model_text: (required) No documentation available.
    """

    model_id: Union[str, "NotSet"]
    model_text: Union[str, "NotSet"]

    def __init__(
        self,
        *,
        model_id: Union[str, "NotSet"] = NOT_SET,
        model_text: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(model_id, NotSet):
            kwargs["model_id"] = model_id
        if not isinstance(model_text, NotSet):
            kwargs["model_text"] = model_text
        super().__init__(kwargs)


class SpanContainingQuery(QueryBase):
    """
    :arg big: (required) Can be any span query. Matching spans from `big`
        that contain matches from `little` are returned.
    :arg little: (required) Can be any span query. Matching spans from
        `big` that contain matches from `little` are returned.
    """

    big: Union["i.SpanQuery", Dict[str, Any], "NotSet"]
    little: Union["i.SpanQuery", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(big, NotSet):
            kwargs["big"] = big
        if not isinstance(little, NotSet):
            kwargs["little"] = little
        super().__init__(**kwargs)


class SpanFieldMaskingQuery(QueryBase):
    """
    :arg field: (required) No documentation available.
    :arg query: (required) No documentation available.
    """

    field: Union[str, "InstrumentedField", "NotSet"]
    query: Union["i.SpanQuery", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        query: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(field, NotSet):
            kwargs["field"] = str(field)
        if not isinstance(query, NotSet):
            kwargs["query"] = query
        super().__init__(**kwargs)


class SpanFirstQuery(QueryBase):
    """
    :arg end: (required) Controls the maximum end position permitted in a
        match.
    :arg match: (required) Can be any other span type query.
    """

    end: Union[int, "NotSet"]
    match: Union["i.SpanQuery", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        end: Union[int, "NotSet"] = NOT_SET,
        match: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(end, NotSet):
            kwargs["end"] = end
        if not isinstance(match, NotSet):
            kwargs["match"] = match
        super().__init__(**kwargs)


class SpanMultiTermQuery(QueryBase):
    """
    :arg match: (required) Should be a multi term query (one of
        `wildcard`, `fuzzy`, `prefix`, `range`, or `regexp` query).
    """

    match: Union[Query, "NotSet"]

    def __init__(self, *, match: Union[Query, "NotSet"] = NOT_SET, **kwargs: Any):
        if not isinstance(match, NotSet):
            kwargs["match"] = match
        super().__init__(**kwargs)


class SpanNearQuery(QueryBase):
    """
    :arg clauses: (required) Array of one or more other span type queries.
    :arg in_order: Controls whether matches are required to be in-order.
    :arg slop: Controls the maximum number of intervening unmatched
        positions permitted.
    """

    clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"]
    in_order: Union[bool, "NotSet"]
    slop: Union[int, "NotSet"]

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        in_order: Union[bool, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(clauses, NotSet):
            kwargs["clauses"] = clauses
        if not isinstance(in_order, NotSet):
            kwargs["in_order"] = in_order
        if not isinstance(slop, NotSet):
            kwargs["slop"] = slop
        super().__init__(**kwargs)


class SpanNotQuery(QueryBase):
    """
    :arg dist: The number of tokens from within the include span that
        can’t have overlap with the exclude span. Equivalent to setting
        both `pre` and `post`.
    :arg exclude: (required) Span query whose matches must not overlap
        those returned.
    :arg include: (required) Span query whose matches are filtered.
    :arg post: The number of tokens after the include span that can’t have
        overlap with the exclude span.
    :arg pre: The number of tokens before the include span that can’t have
        overlap with the exclude span.
    """

    dist: Union[int, "NotSet"]
    exclude: Union["i.SpanQuery", Dict[str, Any], "NotSet"]
    include: Union["i.SpanQuery", Dict[str, Any], "NotSet"]
    post: Union[int, "NotSet"]
    pre: Union[int, "NotSet"]

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
        if not isinstance(dist, NotSet):
            kwargs["dist"] = dist
        if not isinstance(exclude, NotSet):
            kwargs["exclude"] = exclude
        if not isinstance(include, NotSet):
            kwargs["include"] = include
        if not isinstance(post, NotSet):
            kwargs["post"] = post
        if not isinstance(pre, NotSet):
            kwargs["pre"] = pre
        super().__init__(**kwargs)


class SpanOrQuery(QueryBase):
    """
    :arg clauses: (required) Array of one or more other span type queries.
    """

    clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(clauses, NotSet):
            kwargs["clauses"] = clauses
        super().__init__(**kwargs)


class SpanWithinQuery(QueryBase):
    """
    :arg big: (required) Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    :arg little: (required) Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    """

    big: Union["i.SpanQuery", Dict[str, Any], "NotSet"]
    little: Union["i.SpanQuery", Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(big, NotSet):
            kwargs["big"] = big
        if not isinstance(little, NotSet):
            kwargs["little"] = little
        super().__init__(**kwargs)


class HighlightField(HighlightBase):
    """
    :arg fragment_offset: No documentation available.
    :arg matched_fields: No documentation available.
    :arg analyzer: No documentation available.
    """

    fragment_offset: Union[int, "NotSet"]
    matched_fields: Union[
        Union[str, "InstrumentedField"], List[Union[str, "InstrumentedField"]], "NotSet"
    ]
    analyzer: Union[str, Dict[str, Any], "NotSet"]

    def __init__(
        self,
        *,
        fragment_offset: Union[int, "NotSet"] = NOT_SET,
        matched_fields: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        analyzer: Union[str, Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(fragment_offset, NotSet):
            kwargs["fragment_offset"] = fragment_offset
        if not isinstance(matched_fields, NotSet):
            kwargs["matched_fields"] = str(matched_fields)
        if not isinstance(analyzer, NotSet):
            kwargs["analyzer"] = analyzer
        super().__init__(**kwargs)


class GeoDistanceSort(AttrDict[Any]):
    """
    :arg mode: No documentation available.
    :arg distance_type: No documentation available.
    :arg ignore_unmapped: No documentation available.
    :arg order: No documentation available.
    :arg unit: No documentation available.
    :arg nested: No documentation available.
    """

    mode: Union[Literal["min", "max", "sum", "avg", "median"], "NotSet"]
    distance_type: Union[Literal["arc", "plane"], "NotSet"]
    ignore_unmapped: Union[bool, "NotSet"]
    order: Union[Literal["asc", "desc"], "NotSet"]
    unit: Union[Literal["in", "ft", "yd", "mi", "nmi", "km", "m", "cm", "mm"], "NotSet"]
    nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"]

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
        if not isinstance(mode, NotSet):
            kwargs["mode"] = mode
        if not isinstance(distance_type, NotSet):
            kwargs["distance_type"] = distance_type
        if not isinstance(ignore_unmapped, NotSet):
            kwargs["ignore_unmapped"] = ignore_unmapped
        if not isinstance(order, NotSet):
            kwargs["order"] = order
        if not isinstance(unit, NotSet):
            kwargs["unit"] = unit
        if not isinstance(nested, NotSet):
            kwargs["nested"] = nested
        super().__init__(kwargs)


class ScoreSort(AttrDict[Any]):
    """
    :arg order: No documentation available.
    """

    order: Union[Literal["asc", "desc"], "NotSet"]

    def __init__(
        self, *, order: Union[Literal["asc", "desc"], "NotSet"] = NOT_SET, **kwargs: Any
    ):
        if not isinstance(order, NotSet):
            kwargs["order"] = order
        super().__init__(kwargs)


class ScriptSort(AttrDict[Any]):
    """
    :arg order: No documentation available.
    :arg script: (required) No documentation available.
    :arg type: No documentation available.
    :arg mode: No documentation available.
    :arg nested: No documentation available.
    """

    order: Union[Literal["asc", "desc"], "NotSet"]
    script: Union["i.Script", Dict[str, Any], "NotSet"]
    type: Union[Literal["string", "number", "version"], "NotSet"]
    mode: Union[Literal["min", "max", "sum", "avg", "median"], "NotSet"]
    nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"]

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
        if not isinstance(order, NotSet):
            kwargs["order"] = order
        if not isinstance(script, NotSet):
            kwargs["script"] = script
        if not isinstance(type, NotSet):
            kwargs["type"] = type
        if not isinstance(mode, NotSet):
            kwargs["mode"] = mode
        if not isinstance(nested, NotSet):
            kwargs["nested"] = nested
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

    all_of: Union["i.IntervalsAllOf", Dict[str, Any], "NotSet"]
    any_of: Union["i.IntervalsAnyOf", Dict[str, Any], "NotSet"]
    fuzzy: Union["i.IntervalsFuzzy", Dict[str, Any], "NotSet"]
    match: Union["i.IntervalsMatch", Dict[str, Any], "NotSet"]
    prefix: Union["i.IntervalsPrefix", Dict[str, Any], "NotSet"]
    wildcard: Union["i.IntervalsWildcard", Dict[str, Any], "NotSet"]

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
        if not isinstance(all_of, NotSet):
            kwargs["all_of"] = all_of
        if not isinstance(any_of, NotSet):
            kwargs["any_of"] = any_of
        if not isinstance(fuzzy, NotSet):
            kwargs["fuzzy"] = fuzzy
        if not isinstance(match, NotSet):
            kwargs["match"] = match
        if not isinstance(prefix, NotSet):
            kwargs["prefix"] = prefix
        if not isinstance(wildcard, NotSet):
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

    after: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    before: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    contained_by: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    containing: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    not_contained_by: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    not_containing: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    not_overlapping: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    overlapping: Union["i.IntervalsContainer", Dict[str, Any], "NotSet"]
    script: Union["i.Script", Dict[str, Any], "NotSet"]

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
        if not isinstance(after, NotSet):
            kwargs["after"] = after
        if not isinstance(before, NotSet):
            kwargs["before"] = before
        if not isinstance(contained_by, NotSet):
            kwargs["contained_by"] = contained_by
        if not isinstance(containing, NotSet):
            kwargs["containing"] = containing
        if not isinstance(not_contained_by, NotSet):
            kwargs["not_contained_by"] = not_contained_by
        if not isinstance(not_containing, NotSet):
            kwargs["not_containing"] = not_containing
        if not isinstance(not_overlapping, NotSet):
            kwargs["not_overlapping"] = not_overlapping
        if not isinstance(overlapping, NotSet):
            kwargs["overlapping"] = overlapping
        if not isinstance(script, NotSet):
            kwargs["script"] = script
        super().__init__(kwargs)


class NestedSortValue(AttrDict[Any]):
    """
    :arg filter: No documentation available.
    :arg max_children: No documentation available.
    :arg nested: No documentation available.
    :arg path: (required) No documentation available.
    """

    filter: Union[Query, "NotSet"]
    max_children: Union[int, "NotSet"]
    nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"]
    path: Union[str, "InstrumentedField", "NotSet"]

    def __init__(
        self,
        *,
        filter: Union[Query, "NotSet"] = NOT_SET,
        max_children: Union[int, "NotSet"] = NOT_SET,
        nested: Union["i.NestedSortValue", Dict[str, Any], "NotSet"] = NOT_SET,
        path: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(filter, NotSet):
            kwargs["filter"] = filter
        if not isinstance(max_children, NotSet):
            kwargs["max_children"] = max_children
        if not isinstance(nested, NotSet):
            kwargs["nested"] = nested
        if not isinstance(path, NotSet):
            kwargs["path"] = str(path)
        super().__init__(kwargs)
