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

import collections.abc
from copy import deepcopy
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    overload,
)

# 'SF' looks unused but the test suite assumes it's available
# from this module so others are liable to do so as well.
from .function import SF  # noqa: F401
from .function import ScoreFunction
from .utils import NOT_SET, DslBase, NotSet

if TYPE_CHECKING:
    from elasticsearch_dsl import interfaces as i
    from elasticsearch_dsl import wrappers

    from .document_base import InstrumentedField

_T = TypeVar("_T")
_M = TypeVar("_M", bound=Mapping[str, Any])


class QProxiedProtocol(Protocol[_T]):
    _proxied: _T


@overload
def Q(name_or_query: MutableMapping[str, _M]) -> "Query": ...


@overload
def Q(name_or_query: "Query") -> "Query": ...


@overload
def Q(name_or_query: QProxiedProtocol[_T]) -> _T: ...


@overload
def Q(name_or_query: str = "match_all", **params: Any) -> "Query": ...


def Q(
    name_or_query: Union[
        str,
        "Query",
        QProxiedProtocol[_T],
        MutableMapping[str, _M],
    ] = "match_all",
    **params: Any,
) -> Union["Query", _T]:
    # {"match": {"title": "python"}}
    if isinstance(name_or_query, collections.abc.MutableMapping):
        if params:
            raise ValueError("Q() cannot accept parameters when passing in a dict.")
        if len(name_or_query) != 1:
            raise ValueError(
                'Q() can only accept dict with a single query ({"match": {...}}). '
                "Instead it got (%r)" % name_or_query
            )
        name, q_params = deepcopy(name_or_query).popitem()
        return Query.get_dsl_class(name)(_expand__to_dot=False, **q_params)

    # MatchAll()
    if isinstance(name_or_query, Query):
        if params:
            raise ValueError(
                "Q() cannot accept parameters when passing in a Query object."
            )
        return name_or_query

    # s.query = Q('filtered', query=s.query)
    if hasattr(name_or_query, "_proxied"):
        return cast(QProxiedProtocol[_T], name_or_query)._proxied

    # "match", title="python"
    return Query.get_dsl_class(name_or_query)(**params)


class Query(DslBase):
    _type_name = "query"
    _type_shortcut = staticmethod(Q)
    name: ClassVar[Optional[str]] = None

    # Add type annotations for methods not defined in every subclass
    __ror__: ClassVar[Callable[["Query", "Query"], "Query"]]
    __radd__: ClassVar[Callable[["Query", "Query"], "Query"]]
    __rand__: ClassVar[Callable[["Query", "Query"], "Query"]]

    def __add__(self, other: "Query") -> "Query":
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, "__radd__"):
            return other.__radd__(self)
        return Bool(must=[self, other])

    def __invert__(self) -> "Query":
        return Bool(must_not=[self])

    def __or__(self, other: "Query") -> "Query":
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, "__ror__"):
            return other.__ror__(self)
        return Bool(should=[self, other])

    def __and__(self, other: "Query") -> "Query":
        # make sure we give queries that know how to combine themselves
        # preference
        if hasattr(other, "__rand__"):
            return other.__rand__(self)
        return Bool(must=[self, other])


class Bool(Query):
    """
    matches documents matching boolean combinations of other queries.

    :arg filter: The clause (query) must appear in matching documents.
        However, unlike `must`, the score of the query will be ignored.
    :arg minimum_should_match: Specifies the number or percentage of
        `should` clauses returned documents must match.
    :arg must: The clause (query) must appear in matching documents and
        will contribute to the score.
    :arg must_not: The clause (query) must not appear in the matching
        documents. Because scoring is ignored, a score of `0` is returned
        for all documents.
    :arg should: The clause (query) should appear in the matching
        document.
    """

    name = "bool"
    _param_defs = {
        "filter": {"type": "query", "multi": True},
        "must": {"type": "query", "multi": True},
        "must_not": {"type": "query", "multi": True},
        "should": {"type": "query", "multi": True},
    }

    def __init__(
        self,
        *,
        filter: Union[Query, List[Query], "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        must: Union[Query, List[Query], "NotSet"] = NOT_SET,
        must_not: Union[Query, List[Query], "NotSet"] = NOT_SET,
        should: Union[Query, List[Query], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            filter=filter,
            minimum_should_match=minimum_should_match,
            must=must,
            must_not=must_not,
            should=should,
            **kwargs,
        )

    def __add__(self, other: Query) -> "Bool":
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
            q.filter += other.filter
        else:
            q.must.append(other)
        return q

    __radd__ = __add__

    def __or__(self, other: Query) -> Query:
        for q in (self, other):
            if isinstance(q, Bool) and not any(
                (q.must, q.must_not, q.filter, getattr(q, "minimum_should_match", None))
            ):
                other = self if q is other else other
                q = q._clone()
                if isinstance(other, Bool) and not any(
                    (
                        other.must,
                        other.must_not,
                        other.filter,
                        getattr(other, "minimum_should_match", None),
                    )
                ):
                    q.should.extend(other.should)
                else:
                    q.should.append(other)
                return q

        return Bool(should=[self, other])

    __ror__ = __or__

    @property
    def _min_should_match(self) -> int:
        return getattr(
            self,
            "minimum_should_match",
            0 if not self.should or (self.must or self.filter) else 1,
        )

    def __invert__(self) -> Query:
        # Because an empty Bool query is treated like
        # MatchAll the inverse should be MatchNone
        if not any(chain(self.must, self.filter, self.should, self.must_not)):
            return MatchNone()

        negations: List[Query] = []
        for q in chain(self.must, self.filter):
            negations.append(~q)

        for q in self.must_not:
            negations.append(q)

        if self.should and self._min_should_match:
            negations.append(Bool(must_not=self.should[:]))

        if len(negations) == 1:
            return negations[0]
        return Bool(should=negations)

    def __and__(self, other: Query) -> Query:
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.must_not += other.must_not
            q.filter += other.filter
            q.should = []

            # reset minimum_should_match as it will get calculated below
            if "minimum_should_match" in q._params:
                del q._params["minimum_should_match"]

            for qx in (self, other):
                min_should_match = qx._min_should_match
                # TODO: percentages or negative numbers will fail here
                # for now we report an error
                if not isinstance(min_should_match, int) or min_should_match < 0:
                    raise ValueError(
                        "Can only combine queries with positive integer values for minimum_should_match"
                    )
                # all subqueries are required
                if len(qx.should) <= min_should_match:
                    q.must.extend(qx.should)
                # not all of them are required, use it and remember min_should_match
                elif not q.should:
                    q.minimum_should_match = min_should_match
                    q.should = qx.should
                # all queries are optional, just extend should
                elif q._min_should_match == 0 and min_should_match == 0:
                    q.should.extend(qx.should)
                # not all are required, add a should list to the must with proper min_should_match
                else:
                    q.must.append(
                        Bool(should=qx.should, minimum_should_match=min_should_match)
                    )
        else:
            if not (q.must or q.filter) and q.should:
                q._params.setdefault("minimum_should_match", 1)
            q.must.append(other)
        return q

    __rand__ = __and__


class Boosting(Query):
    """
    Returns documents matching a `positive` query while reducing the
    relevance score of documents that also match a `negative` query.

    :arg negative: (required)Query used to decrease the relevance score of
        matching documents.
    :arg positive: (required)Any returned documents must match this query.
    :arg negative_boost: (required)Floating point number between 0 and 1.0
        used to decrease the relevance scores of documents matching the
        `negative` query.
    """

    name = "boosting"
    _param_defs = {
        "negative": {"type": "query"},
        "positive": {"type": "query"},
    }

    def __init__(
        self,
        *,
        negative: Union[Query, "NotSet"] = NOT_SET,
        positive: Union[Query, "NotSet"] = NOT_SET,
        negative_boost: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            negative=negative,
            positive=positive,
            negative_boost=negative_boost,
            **kwargs,
        )


class Common(Query):
    """
    No documentation available.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "common"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.CommonTermsQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class CombinedFields(Query):
    """
    The `combined_fields` query supports searching multiple text fields as
    if their contents had been indexed into one combined field.

    :arg query: (required)Text to search for in the provided `fields`. The
        `combined_fields` query analyzes the provided text before
        performing a search.
    :arg fields: (required)List of fields to search. Field wildcard
        patterns are allowed. Only `text` fields are supported, and they
        must all have the same search `analyzer`.
    :arg auto_generate_synonyms_phrase_query: If true, match phrase
        queries are automatically created for multi-term synonyms.
    :arg operator: Boolean logic used to interpret text in the query
        value.
    :arg minimum_should_match: Minimum number of clauses that must match
        for a document to be returned.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the analyzer removes all tokens, such as when using a `stop`
        filter.
    """

    name = "combined_fields"

    def __init__(
        self,
        *,
        query: Union[str, "NotSet"] = NOT_SET,
        fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"] = NOT_SET,
        auto_generate_synonyms_phrase_query: Union[bool, "NotSet"] = NOT_SET,
        operator: Union[Literal["or", "and"], "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        zero_terms_query: Union[Literal["none", "all"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            query=query,
            fields=fields,
            auto_generate_synonyms_phrase_query=auto_generate_synonyms_phrase_query,
            operator=operator,
            minimum_should_match=minimum_should_match,
            zero_terms_query=zero_terms_query,
            **kwargs,
        )


class ConstantScore(Query):
    """
    Wraps a filter query and returns every matching document with a
    relevance score equal to the `boost` parameter value.

    :arg filter: (required)Filter query you wish to run. Any returned
        documents must match this query. Filter queries do not calculate
        relevance scores. To speed up performance, Elasticsearch
        automatically caches frequently used filter queries.
    """

    name = "constant_score"
    _param_defs = {
        "filter": {"type": "query"},
    }

    def __init__(self, *, filter: Union[Query, "NotSet"] = NOT_SET, **kwargs: Any):
        super().__init__(filter=filter, **kwargs)


class DisMax(Query):
    """
    Returns documents matching one or more wrapped queries, called query
    clauses or clauses. If a returned document matches multiple query
    clauses, the `dis_max` query assigns the document the highest
    relevance score from any matching clause, plus a tie breaking
    increment for any additional matching subqueries.

    :arg queries: (required)One or more query clauses. Returned documents
        must match one or more of these queries. If a document matches
        multiple queries, Elasticsearch uses the highest relevance score.
    :arg tie_breaker: Floating point number between 0 and 1.0 used to
        increase the relevance scores of documents matching multiple query
        clauses.
    """

    name = "dis_max"
    _param_defs = {
        "queries": {"type": "query", "multi": True},
    }

    def __init__(
        self,
        *,
        queries: Union[List[Query], "NotSet"] = NOT_SET,
        tie_breaker: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(queries=queries, tie_breaker=tie_breaker, **kwargs)


class DistanceFeature(Query):
    """
    Boosts the relevance score of documents closer to a provided origin
    date or point. For example, you can use this query to give more weight
    to documents closer to a certain date or location.

    :arg untyped: An instance of ``UntypedDistanceFeatureQuery``.
    :arg geo: An instance of ``GeoDistanceFeatureQuery``.
    :arg date: An instance of ``DateDistanceFeatureQuery``.
    """

    name = "distance_feature"

    def __init__(
        self,
        *,
        untyped: Union["i.UntypedDistanceFeatureQuery", "NotSet"] = NOT_SET,
        geo: Union["i.GeoDistanceFeatureQuery", "NotSet"] = NOT_SET,
        date: Union["i.DateDistanceFeatureQuery", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(untyped, NotSet):
            kwargs = cast(
                Dict[str, Any],
                untyped.to_dict() if hasattr(untyped, "to_dict") else untyped,
            )
        elif not isinstance(geo, NotSet):
            kwargs = cast(
                Dict[str, Any], geo.to_dict() if hasattr(geo, "to_dict") else geo
            )
        elif not isinstance(date, NotSet):
            kwargs = cast(
                Dict[str, Any], date.to_dict() if hasattr(date, "to_dict") else date
            )
        super().__init__(**kwargs)


class Exists(Query):
    """
    Returns documents that contain an indexed value for a field.

    :arg field: (required)Name of the field you wish to search.
    """

    name = "exists"

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(field=field, **kwargs)


class FunctionScore(Query):
    """
    The `function_score` enables you to modify the score of documents that
    are retrieved by a query.

    :arg boost_mode: Defines how he newly computed score is combined with
        the score of the query
    :arg functions: One or more functions that compute a new score for
        each document returned by the query.
    :arg max_boost: Restricts the new score to not exceed the provided
        limit.
    :arg min_score: Excludes documents that do not meet the provided score
        threshold.
    :arg query: A query that determines the documents for which a new
        score is computed.
    :arg score_mode: Specifies how the computed scores are combined
    """

    name = "function_score"
    _param_defs = {
        "query": {"type": "query"},
        "filter": {"type": "query"},
        "functions": {"type": "score_function", "multi": True},
    }

    def __init__(
        self,
        *,
        boost_mode: Union[
            Literal["multiply", "replace", "sum", "avg", "max", "min"], "NotSet"
        ] = NOT_SET,
        functions: Union[
            List["i.FunctionScoreContainer"], Dict[str, Any], "NotSet"
        ] = NOT_SET,
        max_boost: Union[float, "NotSet"] = NOT_SET,
        min_score: Union[float, "NotSet"] = NOT_SET,
        query: Union[Query, "NotSet"] = NOT_SET,
        score_mode: Union[
            Literal["multiply", "sum", "avg", "first", "max", "min"], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        if isinstance(functions, NotSet):
            functions = []
            for name in ScoreFunction._classes:
                if name in kwargs:
                    functions.append({name: kwargs.pop(name)})  # type: ignore
        super().__init__(
            boost_mode=boost_mode,
            functions=functions,
            max_boost=max_boost,
            min_score=min_score,
            query=query,
            score_mode=score_mode,
            **kwargs,
        )


class Fuzzy(Query):
    """
    Returns documents that contain terms similar to the search term, as
    measured by a Levenshtein edit distance.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "fuzzy"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.FuzzyQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class GeoBoundingBox(Query):
    """
    Matches geo_point and geo_shape values that intersect a bounding box.

    :arg type: No documentation available.
    :arg validation_method: Set to `IGNORE_MALFORMED` to accept geo points
        with invalid latitude or longitude. Set to `COERCE` to also try to
        infer correct latitude or longitude.
    :arg ignore_unmapped: Set to `true` to ignore an unmapped field and
        not match any documents for this query. Set to `false` to throw an
        exception if the field is not mapped.
    """

    name = "geo_bounding_box"

    def __init__(
        self,
        *,
        type: Union[Literal["memory", "indexed"], "NotSet"] = NOT_SET,
        validation_method: Union[
            Literal["coerce", "ignore_malformed", "strict"], "NotSet"
        ] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            type=type,
            validation_method=validation_method,
            ignore_unmapped=ignore_unmapped,
            **kwargs,
        )


class GeoDistance(Query):
    """
    Matches `geo_point` and `geo_shape` values within a given distance of
    a geopoint.

    :arg distance: (required)The radius of the circle centred on the
        specified location. Points which fall into this circle are
        considered to be matches.
    :arg distance_type: How to compute the distance. Set to `plane` for a
        faster calculation that's inaccurate on long distances and close
        to the poles.
    :arg validation_method: Set to `IGNORE_MALFORMED` to accept geo points
        with invalid latitude or longitude. Set to `COERCE` to also try to
        infer correct latitude or longitude.
    :arg ignore_unmapped: Set to `true` to ignore an unmapped field and
        not match any documents for this query. Set to `false` to throw an
        exception if the field is not mapped.
    """

    name = "geo_distance"

    def __init__(
        self,
        *,
        distance: Union[str, "NotSet"] = NOT_SET,
        distance_type: Union[Literal["arc", "plane"], "NotSet"] = NOT_SET,
        validation_method: Union[
            Literal["coerce", "ignore_malformed", "strict"], "NotSet"
        ] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            distance=distance,
            distance_type=distance_type,
            validation_method=validation_method,
            ignore_unmapped=ignore_unmapped,
            **kwargs,
        )


class GeoPolygon(Query):
    """
    No documentation available.

    :arg validation_method: No documentation available.
    :arg ignore_unmapped: No documentation available.
    """

    name = "geo_polygon"

    def __init__(
        self,
        *,
        validation_method: Union[
            Literal["coerce", "ignore_malformed", "strict"], "NotSet"
        ] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            validation_method=validation_method,
            ignore_unmapped=ignore_unmapped,
            **kwargs,
        )


class GeoShape(Query):
    """
    Filter documents indexed using either the `geo_shape` or the
    `geo_point` type.

    :arg ignore_unmapped: Set to `true` to ignore an unmapped field and
        not match any documents for this query. Set to `false` to throw an
        exception if the field is not mapped.
    """

    name = "geo_shape"

    def __init__(
        self, *, ignore_unmapped: Union[bool, "NotSet"] = NOT_SET, **kwargs: Any
    ):
        super().__init__(ignore_unmapped=ignore_unmapped, **kwargs)


class HasChild(Query):
    """
    Returns parent documents whose joined child documents match a provided
    query.

    :arg query: (required)Query you wish to run on child documents of the
        `type` field. If a child document matches the search, the query
        returns the parent document.
    :arg type: (required)Name of the child relationship mapped for the
        `join` field.
    :arg ignore_unmapped: Indicates whether to ignore an unmapped `type`
        and not return any documents instead of an error.
    :arg inner_hits: If defined, each search hit will contain inner hits.
    :arg max_children: Maximum number of child documents that match the
        query allowed for a returned parent document. If the parent
        document exceeds this limit, it is excluded from the search
        results.
    :arg min_children: Minimum number of child documents that match the
        query required to match the query for a returned parent document.
        If the parent document does not meet this limit, it is excluded
        from the search results.
    :arg score_mode: Indicates how scores for matching child documents
        affect the root parent document’s relevance score.
    """

    name = "has_child"
    _param_defs = {
        "query": {"type": "query"},
    }

    def __init__(
        self,
        *,
        query: Union[Query, "NotSet"] = NOT_SET,
        type: Union[str, "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        inner_hits: Union["i.InnerHits", Dict[str, Any], "NotSet"] = NOT_SET,
        max_children: Union[int, "NotSet"] = NOT_SET,
        min_children: Union[int, "NotSet"] = NOT_SET,
        score_mode: Union[
            Literal["none", "avg", "sum", "max", "min"], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            query=query,
            type=type,
            ignore_unmapped=ignore_unmapped,
            inner_hits=inner_hits,
            max_children=max_children,
            min_children=min_children,
            score_mode=score_mode,
            **kwargs,
        )


class HasParent(Query):
    """
    Returns child documents whose joined parent document matches a
    provided query.

    :arg parent_type: (required)Name of the parent relationship mapped for
        the `join` field.
    :arg query: (required)Query you wish to run on parent documents of the
        `parent_type` field. If a parent document matches the search, the
        query returns its child documents.
    :arg ignore_unmapped: Indicates whether to ignore an unmapped
        `parent_type` and not return any documents instead of an error.
        You can use this parameter to query multiple indices that may not
        contain the `parent_type`.
    :arg inner_hits: If defined, each search hit will contain inner hits.
    :arg score: Indicates whether the relevance score of a matching parent
        document is aggregated into its child documents.
    """

    name = "has_parent"
    _param_defs = {
        "query": {"type": "query"},
    }

    def __init__(
        self,
        *,
        parent_type: Union[str, "NotSet"] = NOT_SET,
        query: Union[Query, "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        inner_hits: Union["i.InnerHits", Dict[str, Any], "NotSet"] = NOT_SET,
        score: Union[bool, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            parent_type=parent_type,
            query=query,
            ignore_unmapped=ignore_unmapped,
            inner_hits=inner_hits,
            score=score,
            **kwargs,
        )


class Ids(Query):
    """
    Returns documents based on their IDs. This query uses document IDs
    stored in the `_id` field.

    :arg values: An array of document IDs.
    """

    name = "ids"

    def __init__(
        self, *, values: Union[str, List[str], "NotSet"] = NOT_SET, **kwargs: Any
    ):
        super().__init__(values=values, **kwargs)


class Intervals(Query):
    """
    Returns documents based on the order and proximity of matching terms.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "intervals"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.IntervalsQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class Knn(Query):
    """
    Finds the k nearest vectors to a query vector, as measured by a
    similarity metric. knn query finds nearest vectors through approximate
    search on indexed dense_vectors.

    :arg field: (required)The name of the vector field to search against
    :arg query_vector: The query vector
    :arg query_vector_builder: The query vector builder. You must provide
        a query_vector_builder or query_vector, but not both.
    :arg num_candidates: The number of nearest neighbor candidates to
        consider per shard
    :arg k: The final number of nearest neighbors to return as top hits
    :arg filter: Filters for the kNN search query
    :arg similarity: The minimum similarity for a vector to be considered
        a match
    """

    name = "knn"
    _param_defs = {
        "filter": {"type": "query", "multi": True},
    }

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        query_vector: Union[List[float], "NotSet"] = NOT_SET,
        query_vector_builder: Union[
            "i.QueryVectorBuilder", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        num_candidates: Union[int, "NotSet"] = NOT_SET,
        k: Union[int, "NotSet"] = NOT_SET,
        filter: Union[Query, List[Query], "NotSet"] = NOT_SET,
        similarity: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            field=field,
            query_vector=query_vector,
            query_vector_builder=query_vector_builder,
            num_candidates=num_candidates,
            k=k,
            filter=filter,
            similarity=similarity,
            **kwargs,
        )


class Match(Query):
    """
    Returns documents that match a provided text, number, date or boolean
    value. The provided text is analyzed before matching.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "match"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.MatchQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class MatchAll(Query):
    """
    Matches all documents, giving them all a `_score` of 1.0.
    """

    name = "match_all"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def __add__(self, other: "Query") -> "Query":
        return other._clone()

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: "Query") -> "MatchAll":
        return self

    __ror__ = __or__

    def __invert__(self) -> "MatchNone":
        return MatchNone()


EMPTY_QUERY = MatchAll()


class MatchBoolPrefix(Query):
    """
    Analyzes its input and constructs a `bool` query from the terms. Each
    term except the last is used in a `term` query. The last term is used
    in a prefix query.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "match_bool_prefix"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.MatchBoolPrefixQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class MatchNone(Query):
    """
    Matches no documents.
    """

    name = "match_none"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def __add__(self, other: "Query") -> "MatchNone":
        return self

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: "Query") -> "Query":
        return other._clone()

    __ror__ = __or__

    def __invert__(self) -> MatchAll:
        return MatchAll()


class MatchPhrase(Query):
    """
    Analyzes the text and creates a phrase query out of the analyzed text.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "match_phrase"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.MatchPhraseQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class MatchPhrasePrefix(Query):
    """
    Returns documents that contain the words of a provided text, in the
    same order as provided. The last term of the provided text is treated
    as a prefix, matching any words that begin with that term.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "match_phrase_prefix"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.MatchPhrasePrefixQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class MoreLikeThis(Query):
    """
    Returns documents that are "like" a given set of documents.

    :arg like: (required)Specifies free form text and/or a single or
        multiple documents for which you want to find similar documents.
    :arg analyzer: The analyzer that is used to analyze the free form
        text. Defaults to the analyzer associated with the first field in
        fields.
    :arg boost_terms: Each term in the formed query could be further
        boosted by their tf-idf score. This sets the boost factor to use
        when using this feature. Defaults to deactivated (0).
    :arg fail_on_unsupported_field: Controls whether the query should fail
        (throw an exception) if any of the specified fields are not of the
        supported types (`text` or `keyword`).
    :arg fields: A list of fields to fetch and analyze the text from.
        Defaults to the `index.query.default_field` index setting, which
        has a default value of `*`.
    :arg include: Specifies whether the input documents should also be
        included in the search results returned.
    :arg max_doc_freq: The maximum document frequency above which the
        terms are ignored from the input document.
    :arg max_query_terms: The maximum number of query terms that can be
        selected.
    :arg max_word_length: The maximum word length above which the terms
        are ignored. Defaults to unbounded (`0`).
    :arg min_doc_freq: The minimum document frequency below which the
        terms are ignored from the input document.
    :arg minimum_should_match: After the disjunctive query has been
        formed, this parameter controls the number of terms that must
        match.
    :arg min_term_freq: The minimum term frequency below which the terms
        are ignored from the input document.
    :arg min_word_length: The minimum word length below which the terms
        are ignored.
    :arg routing: No documentation available.
    :arg stop_words: An array of stop words. Any word in this set is
        ignored.
    :arg unlike: Used in combination with `like` to exclude documents that
        match a set of terms.
    :arg version: No documentation available.
    :arg version_type: No documentation available.
    """

    name = "more_like_this"

    def __init__(
        self,
        *,
        like: Union[
            Union[str, "i.LikeDocument"],
            List[Union[str, "i.LikeDocument"]],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        boost_terms: Union[float, "NotSet"] = NOT_SET,
        fail_on_unsupported_field: Union[bool, "NotSet"] = NOT_SET,
        fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"] = NOT_SET,
        include: Union[bool, "NotSet"] = NOT_SET,
        max_doc_freq: Union[int, "NotSet"] = NOT_SET,
        max_query_terms: Union[int, "NotSet"] = NOT_SET,
        max_word_length: Union[int, "NotSet"] = NOT_SET,
        min_doc_freq: Union[int, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        min_term_freq: Union[int, "NotSet"] = NOT_SET,
        min_word_length: Union[int, "NotSet"] = NOT_SET,
        routing: Union[str, "NotSet"] = NOT_SET,
        stop_words: Union[str, List[str], "NotSet"] = NOT_SET,
        unlike: Union[
            Union[str, "i.LikeDocument"],
            List[Union[str, "i.LikeDocument"]],
            Dict[str, Any],
            "NotSet",
        ] = NOT_SET,
        version: Union[int, "NotSet"] = NOT_SET,
        version_type: Union[
            Literal["internal", "external", "external_gte", "force"], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            like=like,
            analyzer=analyzer,
            boost_terms=boost_terms,
            fail_on_unsupported_field=fail_on_unsupported_field,
            fields=fields,
            include=include,
            max_doc_freq=max_doc_freq,
            max_query_terms=max_query_terms,
            max_word_length=max_word_length,
            min_doc_freq=min_doc_freq,
            minimum_should_match=minimum_should_match,
            min_term_freq=min_term_freq,
            min_word_length=min_word_length,
            routing=routing,
            stop_words=stop_words,
            unlike=unlike,
            version=version,
            version_type=version_type,
            **kwargs,
        )


class MultiMatch(Query):
    """
    Enables you to search for a provided text, number, date or boolean
    value across multiple fields. The provided text is analyzed before
    matching.

    :arg query: (required)Text, number, boolean value or date you wish to
        find in the provided field.
    :arg analyzer: Analyzer used to convert the text in the query value
        into tokens.
    :arg auto_generate_synonyms_phrase_query: If `true`, match phrase
        queries are automatically created for multi-term synonyms.
    :arg cutoff_frequency: No documentation available.
    :arg fields: The fields to be queried. Defaults to the
        `index.query.default_field` index settings, which in turn defaults
        to `*`.
    :arg fuzziness: Maximum edit distance allowed for matching.
    :arg fuzzy_rewrite: Method used to rewrite the query.
    :arg fuzzy_transpositions: If `true`, edits for fuzzy matching include
        transpositions of two adjacent characters (for example, `ab` to
        `ba`). Can be applied to the term subqueries constructed for all
        terms but the final term.
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
    :arg slop: Maximum number of positions allowed between matching
        tokens.
    :arg tie_breaker: Determines how scores for each per-term blended
        query and scores across groups are combined.
    :arg type: How `the` multi_match query is executed internally.
    :arg zero_terms_query: Indicates whether no documents are returned if
        the `analyzer` removes all tokens, such as when using a `stop`
        filter.
    """

    name = "multi_match"

    def __init__(
        self,
        *,
        query: Union[str, "NotSet"] = NOT_SET,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        auto_generate_synonyms_phrase_query: Union[bool, "NotSet"] = NOT_SET,
        cutoff_frequency: Union[float, "NotSet"] = NOT_SET,
        fields: Union[
            Union[str, "InstrumentedField"],
            List[Union[str, "InstrumentedField"]],
            "NotSet",
        ] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        fuzzy_rewrite: Union[str, "NotSet"] = NOT_SET,
        fuzzy_transpositions: Union[bool, "NotSet"] = NOT_SET,
        lenient: Union[bool, "NotSet"] = NOT_SET,
        max_expansions: Union[int, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        prefix_length: Union[int, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        tie_breaker: Union[float, "NotSet"] = NOT_SET,
        type: Union[
            Literal[
                "best_fields",
                "most_fields",
                "cross_fields",
                "phrase",
                "phrase_prefix",
                "bool_prefix",
            ],
            "NotSet",
        ] = NOT_SET,
        zero_terms_query: Union[Literal["all", "none"], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            query=query,
            analyzer=analyzer,
            auto_generate_synonyms_phrase_query=auto_generate_synonyms_phrase_query,
            cutoff_frequency=cutoff_frequency,
            fields=fields,
            fuzziness=fuzziness,
            fuzzy_rewrite=fuzzy_rewrite,
            fuzzy_transpositions=fuzzy_transpositions,
            lenient=lenient,
            max_expansions=max_expansions,
            minimum_should_match=minimum_should_match,
            operator=operator,
            prefix_length=prefix_length,
            slop=slop,
            tie_breaker=tie_breaker,
            type=type,
            zero_terms_query=zero_terms_query,
            **kwargs,
        )


class Nested(Query):
    """
    Wraps another query to search nested fields. If an object matches the
    search, the nested query returns the root parent document.

    :arg path: (required)Path to the nested object you wish to search.
    :arg query: (required)Query you wish to run on nested objects in the
        path.
    :arg ignore_unmapped: Indicates whether to ignore an unmapped path and
        not return any documents instead of an error.
    :arg inner_hits: If defined, each search hit will contain inner hits.
    :arg score_mode: How scores for matching child objects affect the root
        parent document’s relevance score.
    """

    name = "nested"
    _param_defs = {
        "query": {"type": "query"},
    }

    def __init__(
        self,
        *,
        path: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        query: Union[Query, "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        inner_hits: Union["i.InnerHits", Dict[str, Any], "NotSet"] = NOT_SET,
        score_mode: Union[
            Literal["none", "avg", "sum", "max", "min"], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            path=path,
            query=query,
            ignore_unmapped=ignore_unmapped,
            inner_hits=inner_hits,
            score_mode=score_mode,
            **kwargs,
        )


class ParentId(Query):
    """
    Returns child documents joined to a specific parent document.

    :arg id: ID of the parent document.
    :arg ignore_unmapped: Indicates whether to ignore an unmapped `type`
        and not return any documents instead of an error.
    :arg type: Name of the child relationship mapped for the `join` field.
    """

    name = "parent_id"

    def __init__(
        self,
        *,
        id: Union[str, "NotSet"] = NOT_SET,
        ignore_unmapped: Union[bool, "NotSet"] = NOT_SET,
        type: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(id=id, ignore_unmapped=ignore_unmapped, type=type, **kwargs)


class Percolate(Query):
    """
    Matches queries stored in an index.

    :arg field: (required)Field that holds the indexed queries. The field
        must use the `percolator` mapping type.
    :arg document: The source of the document being percolated.
    :arg documents: An array of sources of the documents being percolated.
    :arg id: The ID of a stored document to percolate.
    :arg index: The index of a stored document to percolate.
    :arg name: The suffix used for the `_percolator_document_slot` field
        when multiple `percolate` queries are specified.
    :arg preference: Preference used to fetch document to percolate.
    :arg routing: Routing used to fetch document to percolate.
    :arg version: The expected version of a stored document to percolate.
    """

    name = "percolate"

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        document: Any = NOT_SET,
        documents: Union[List[Any], "NotSet"] = NOT_SET,
        id: Union[str, "NotSet"] = NOT_SET,
        index: Union[str, "NotSet"] = NOT_SET,
        name: Union[str, "NotSet"] = NOT_SET,
        preference: Union[str, "NotSet"] = NOT_SET,
        routing: Union[str, "NotSet"] = NOT_SET,
        version: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            field=field,
            document=document,
            documents=documents,
            id=id,
            index=index,
            name=name,
            preference=preference,
            routing=routing,
            version=version,
            **kwargs,
        )


class Pinned(Query):
    """
    Promotes selected documents to rank higher than those matching a given
    query.

    :arg organic: (required)Any choice of query used to rank documents
        which will be ranked below the "pinned" documents.
    :arg ids: Document IDs listed in the order they are to appear in
        results. Required if `docs` is not specified.
    :arg docs: Documents listed in the order they are to appear in
        results. Required if `ids` is not specified.
    """

    name = "pinned"
    _param_defs = {
        "organic": {"type": "query"},
    }

    def __init__(
        self,
        *,
        organic: Union[Query, "NotSet"] = NOT_SET,
        ids: Union[List[str], "NotSet"] = NOT_SET,
        docs: Union[List["i.PinnedDoc"], Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(organic=organic, ids=ids, docs=docs, **kwargs)


class Prefix(Query):
    """
    Returns documents that contain a specific prefix in a provided field.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "prefix"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.PrefixQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class QueryString(Query):
    """
    Returns documents based on a provided query string, using a parser
    with a strict syntax.

    :arg query: (required)Query string you wish to parse and use for
        search.
    :arg allow_leading_wildcard: If `true`, the wildcard characters `*`
        and `?` are allowed as the first character of the query string.
    :arg analyzer: Analyzer used to convert text in the query string into
        tokens.
    :arg analyze_wildcard: If `true`, the query attempts to analyze
        wildcard terms in the query string.
    :arg auto_generate_synonyms_phrase_query: If `true`, match phrase
        queries are automatically created for multi-term synonyms.
    :arg default_field: Default field to search if no field is provided in
        the query string. Supports wildcards (`*`). Defaults to the
        `index.query.default_field` index setting, which has a default
        value of `*`.
    :arg default_operator: Default boolean logic used to interpret text in
        the query string if no operators are specified.
    :arg enable_position_increments: If `true`, enable position increments
        in queries constructed from a `query_string` search.
    :arg escape: No documentation available.
    :arg fields: Array of fields to search. Supports wildcards (`*`).
    :arg fuzziness: Maximum edit distance allowed for fuzzy matching.
    :arg fuzzy_max_expansions: Maximum number of terms to which the query
        expands for fuzzy matching.
    :arg fuzzy_prefix_length: Number of beginning characters left
        unchanged for fuzzy matching.
    :arg fuzzy_rewrite: Method used to rewrite the query.
    :arg fuzzy_transpositions: If `true`, edits for fuzzy matching include
        transpositions of two adjacent characters (for example, `ab` to
        `ba`).
    :arg lenient: If `true`, format-based errors, such as providing a text
        value for a numeric field, are ignored.
    :arg max_determinized_states: Maximum number of automaton states
        required for the query.
    :arg minimum_should_match: Minimum number of clauses that must match
        for a document to be returned.
    :arg phrase_slop: Maximum number of positions allowed between matching
        tokens for phrases.
    :arg quote_analyzer: Analyzer used to convert quoted text in the query
        string into tokens. For quoted text, this parameter overrides the
        analyzer specified in the `analyzer` parameter.
    :arg quote_field_suffix: Suffix appended to quoted text in the query
        string. You can use this suffix to use a different analysis method
        for exact matches.
    :arg rewrite: Method used to rewrite the query.
    :arg tie_breaker: How to combine the queries generated from the
        individual search terms in the resulting `dis_max` query.
    :arg time_zone: Coordinated Universal Time (UTC) offset or IANA time
        zone used to convert date values in the query string to UTC.
    :arg type: Determines how the query matches and scores documents.
    """

    name = "query_string"

    def __init__(
        self,
        *,
        query: Union[str, "NotSet"] = NOT_SET,
        allow_leading_wildcard: Union[bool, "NotSet"] = NOT_SET,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        analyze_wildcard: Union[bool, "NotSet"] = NOT_SET,
        auto_generate_synonyms_phrase_query: Union[bool, "NotSet"] = NOT_SET,
        default_field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        default_operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        enable_position_increments: Union[bool, "NotSet"] = NOT_SET,
        escape: Union[bool, "NotSet"] = NOT_SET,
        fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"] = NOT_SET,
        fuzziness: Union[str, int, "NotSet"] = NOT_SET,
        fuzzy_max_expansions: Union[int, "NotSet"] = NOT_SET,
        fuzzy_prefix_length: Union[int, "NotSet"] = NOT_SET,
        fuzzy_rewrite: Union[str, "NotSet"] = NOT_SET,
        fuzzy_transpositions: Union[bool, "NotSet"] = NOT_SET,
        lenient: Union[bool, "NotSet"] = NOT_SET,
        max_determinized_states: Union[int, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        phrase_slop: Union[float, "NotSet"] = NOT_SET,
        quote_analyzer: Union[str, "NotSet"] = NOT_SET,
        quote_field_suffix: Union[str, "NotSet"] = NOT_SET,
        rewrite: Union[str, "NotSet"] = NOT_SET,
        tie_breaker: Union[float, "NotSet"] = NOT_SET,
        time_zone: Union[str, "NotSet"] = NOT_SET,
        type: Union[
            Literal[
                "best_fields",
                "most_fields",
                "cross_fields",
                "phrase",
                "phrase_prefix",
                "bool_prefix",
            ],
            "NotSet",
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            query=query,
            allow_leading_wildcard=allow_leading_wildcard,
            analyzer=analyzer,
            analyze_wildcard=analyze_wildcard,
            auto_generate_synonyms_phrase_query=auto_generate_synonyms_phrase_query,
            default_field=default_field,
            default_operator=default_operator,
            enable_position_increments=enable_position_increments,
            escape=escape,
            fields=fields,
            fuzziness=fuzziness,
            fuzzy_max_expansions=fuzzy_max_expansions,
            fuzzy_prefix_length=fuzzy_prefix_length,
            fuzzy_rewrite=fuzzy_rewrite,
            fuzzy_transpositions=fuzzy_transpositions,
            lenient=lenient,
            max_determinized_states=max_determinized_states,
            minimum_should_match=minimum_should_match,
            phrase_slop=phrase_slop,
            quote_analyzer=quote_analyzer,
            quote_field_suffix=quote_field_suffix,
            rewrite=rewrite,
            tie_breaker=tie_breaker,
            time_zone=time_zone,
            type=type,
            **kwargs,
        )


class Range(Query):
    """
    Returns documents that contain terms within a provided range.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "range"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["wrappers.Range[Any]", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class RankFeature(Query):
    """
    Boosts the relevance score of documents based on the numeric value of
    a `rank_feature` or `rank_features` field.

    :arg field: (required)`rank_feature` or `rank_features` field used to
        boost relevance scores.
    :arg saturation: Saturation function used to boost relevance scores
        based on the value of the rank feature `field`.
    :arg log: Logarithmic function used to boost relevance scores based on
        the value of the rank feature `field`.
    :arg linear: Linear function used to boost relevance scores based on
        the value of the rank feature `field`.
    :arg sigmoid: Sigmoid function used to boost relevance scores based on
        the value of the rank feature `field`.
    """

    name = "rank_feature"

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        saturation: Union[
            "i.RankFeatureFunctionSaturation", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        log: Union[
            "i.RankFeatureFunctionLogarithm", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        linear: Union[
            "i.RankFeatureFunctionLinear", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        sigmoid: Union[
            "i.RankFeatureFunctionSigmoid", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            field=field,
            saturation=saturation,
            log=log,
            linear=linear,
            sigmoid=sigmoid,
            **kwargs,
        )


class Regexp(Query):
    """
    Returns documents that contain terms matching a regular expression.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "regexp"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.RegexpQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class Rule(Query):
    """
    No documentation available.

    :arg ruleset_ids: (required)No documentation available.
    :arg match_criteria: (required)No documentation available.
    :arg organic: (required)No documentation available.
    """

    name = "rule"
    _param_defs = {
        "organic": {"type": "query"},
    }

    def __init__(
        self,
        *,
        ruleset_ids: Union[List[str], "NotSet"] = NOT_SET,
        match_criteria: Any = NOT_SET,
        organic: Union[Query, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            ruleset_ids=ruleset_ids,
            match_criteria=match_criteria,
            organic=organic,
            **kwargs,
        )


class Script(Query):
    """
    Filters documents based on a provided script. The script query is
    typically used in a filter context.

    :arg script: (required)Contains a script to run as a query. This
        script must return a boolean value, `true` or `false`.
    """

    name = "script"

    def __init__(
        self,
        *,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(script=script, **kwargs)


class ScriptScore(Query):
    """
    Uses a script to provide a custom score for returned documents.

    :arg query: (required)Query used to return documents.
    :arg script: (required)Script used to compute the score of documents
        returned by the query. Important: final relevance scores from the
        `script_score` query cannot be negative.
    :arg min_score: Documents with a score lower than this floating point
        number are excluded from the search results.
    """

    name = "script_score"
    _param_defs = {
        "query": {"type": "query"},
    }

    def __init__(
        self,
        *,
        query: Union[Query, "NotSet"] = NOT_SET,
        script: Union["i.Script", Dict[str, Any], "NotSet"] = NOT_SET,
        min_score: Union[float, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(query=query, script=script, min_score=min_score, **kwargs)


class Semantic(Query):
    """
    A semantic query to semantic_text field types

    :arg query: (required)The query text
    :arg field: (required)The field to query, which must be a
        semantic_text field type
    """

    name = "semantic"

    def __init__(
        self,
        *,
        query: Union[str, "NotSet"] = NOT_SET,
        field: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(query=query, field=field, **kwargs)


class Shape(Query):
    """
    Queries documents that contain fields indexed using the `shape` type.

    :arg ignore_unmapped: When set to `true` the query ignores an unmapped
        field and will not match any documents.
    """

    name = "shape"

    def __init__(
        self, *, ignore_unmapped: Union[bool, "NotSet"] = NOT_SET, **kwargs: Any
    ):
        super().__init__(ignore_unmapped=ignore_unmapped, **kwargs)


class SimpleQueryString(Query):
    """
    Returns documents based on a provided query string, using a parser
    with a limited but fault-tolerant syntax.

    :arg query: (required)Query string in the simple query string syntax
        you wish to parse and use for search.
    :arg analyzer: Analyzer used to convert text in the query string into
        tokens.
    :arg analyze_wildcard: If `true`, the query attempts to analyze
        wildcard terms in the query string.
    :arg auto_generate_synonyms_phrase_query: If `true`, the parser
        creates a match_phrase query for each multi-position token.
    :arg default_operator: Default boolean logic used to interpret text in
        the query string if no operators are specified.
    :arg fields: Array of fields you wish to search. Accepts wildcard
        expressions. You also can boost relevance scores for matches to
        particular fields using a caret (`^`) notation. Defaults to the
        `index.query.default_field index` setting, which has a default
        value of `*`.
    :arg flags: List of enabled operators for the simple query string
        syntax.
    :arg fuzzy_max_expansions: Maximum number of terms to which the query
        expands for fuzzy matching.
    :arg fuzzy_prefix_length: Number of beginning characters left
        unchanged for fuzzy matching.
    :arg fuzzy_transpositions: If `true`, edits for fuzzy matching include
        transpositions of two adjacent characters (for example, `ab` to
        `ba`).
    :arg lenient: If `true`, format-based errors, such as providing a text
        value for a numeric field, are ignored.
    :arg minimum_should_match: Minimum number of clauses that must match
        for a document to be returned.
    :arg quote_field_suffix: Suffix appended to quoted text in the query
        string.
    """

    name = "simple_query_string"

    def __init__(
        self,
        *,
        query: Union[str, "NotSet"] = NOT_SET,
        analyzer: Union[str, "NotSet"] = NOT_SET,
        analyze_wildcard: Union[bool, "NotSet"] = NOT_SET,
        auto_generate_synonyms_phrase_query: Union[bool, "NotSet"] = NOT_SET,
        default_operator: Union[Literal["and", "or"], "NotSet"] = NOT_SET,
        fields: Union[List[Union[str, "InstrumentedField"]], "NotSet"] = NOT_SET,
        flags: Union["i.PipeSeparatedFlags", Dict[str, Any], "NotSet"] = NOT_SET,
        fuzzy_max_expansions: Union[int, "NotSet"] = NOT_SET,
        fuzzy_prefix_length: Union[int, "NotSet"] = NOT_SET,
        fuzzy_transpositions: Union[bool, "NotSet"] = NOT_SET,
        lenient: Union[bool, "NotSet"] = NOT_SET,
        minimum_should_match: Union[int, str, "NotSet"] = NOT_SET,
        quote_field_suffix: Union[str, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            query=query,
            analyzer=analyzer,
            analyze_wildcard=analyze_wildcard,
            auto_generate_synonyms_phrase_query=auto_generate_synonyms_phrase_query,
            default_operator=default_operator,
            fields=fields,
            flags=flags,
            fuzzy_max_expansions=fuzzy_max_expansions,
            fuzzy_prefix_length=fuzzy_prefix_length,
            fuzzy_transpositions=fuzzy_transpositions,
            lenient=lenient,
            minimum_should_match=minimum_should_match,
            quote_field_suffix=quote_field_suffix,
            **kwargs,
        )


class SpanContaining(Query):
    """
    Returns matches which enclose another span query.

    :arg little: (required)Can be any span query. Matching spans from
        `big` that contain matches from `little` are returned.
    :arg big: (required)Can be any span query. Matching spans from `big`
        that contain matches from `little` are returned.
    """

    name = "span_containing"

    def __init__(
        self,
        *,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(little=little, big=big, **kwargs)


class SpanFieldMasking(Query):
    """
    Wrapper to allow span queries to participate in composite single-field
    span queries by _lying_ about their search field.

    :arg query: (required)No documentation available.
    :arg field: (required)No documentation available.
    """

    name = "span_field_masking"

    def __init__(
        self,
        *,
        query: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(query=query, field=field, **kwargs)


class SpanFirst(Query):
    """
    Matches spans near the beginning of a field.

    :arg match: (required)Can be any other span type query.
    :arg end: (required)Controls the maximum end position permitted in a
        match.
    """

    name = "span_first"

    def __init__(
        self,
        *,
        match: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        end: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(match=match, end=end, **kwargs)


class SpanMulti(Query):
    """
    Allows you to wrap a multi term query (one of `wildcard`, `fuzzy`,
    `prefix`, `range`, or `regexp` query) as a `span` query, so it can be
    nested.

    :arg match: (required)Should be a multi term query (one of `wildcard`,
        `fuzzy`, `prefix`, `range`, or `regexp` query).
    """

    name = "span_multi"
    _param_defs = {
        "match": {"type": "query"},
    }

    def __init__(self, *, match: Union[Query, "NotSet"] = NOT_SET, **kwargs: Any):
        super().__init__(match=match, **kwargs)


class SpanNear(Query):
    """
    Matches spans which are near one another. You can specify `slop`, the
    maximum number of intervening unmatched positions, as well as whether
    matches are required to be in-order.

    :arg clauses: (required)Array of one or more other span type queries.
    :arg in_order: Controls whether matches are required to be in-order.
    :arg slop: Controls the maximum number of intervening unmatched
        positions permitted.
    """

    name = "span_near"

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        in_order: Union[bool, "NotSet"] = NOT_SET,
        slop: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(clauses=clauses, in_order=in_order, slop=slop, **kwargs)


class SpanNot(Query):
    """
    Removes matches which overlap with another span query or which are
    within x tokens before (controlled by the parameter `pre`) or y tokens
    after (controlled by the parameter `post`) another span query.

    :arg exclude: (required)Span query whose matches must not overlap
        those returned.
    :arg include: (required)Span query whose matches are filtered.
    :arg dist: The number of tokens from within the include span that
        can’t have overlap with the exclude span. Equivalent to setting
        both `pre` and `post`.
    :arg post: The number of tokens after the include span that can’t have
        overlap with the exclude span.
    :arg pre: The number of tokens before the include span that can’t have
        overlap with the exclude span.
    """

    name = "span_not"

    def __init__(
        self,
        *,
        exclude: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        include: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        dist: Union[int, "NotSet"] = NOT_SET,
        post: Union[int, "NotSet"] = NOT_SET,
        pre: Union[int, "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            exclude=exclude, include=include, dist=dist, post=post, pre=pre, **kwargs
        )


class SpanOr(Query):
    """
    Matches the union of its span clauses.

    :arg clauses: (required)Array of one or more other span type queries.
    """

    name = "span_or"

    def __init__(
        self,
        *,
        clauses: Union[List["i.SpanQuery"], Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(clauses=clauses, **kwargs)


class SpanTerm(Query):
    """
    Matches spans containing a term.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "span_term"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.SpanTermQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class SpanWithin(Query):
    """
    Returns matches which are enclosed inside another span query.

    :arg little: (required)Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    :arg big: (required)Can be any span query. Matching spans from
        `little` that are enclosed within `big` are returned.
    """

    name = "span_within"

    def __init__(
        self,
        *,
        little: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        big: Union["i.SpanQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(little=little, big=big, **kwargs)


class SparseVector(Query):
    """
    Using input query vectors or a natural language processing model to
    convert a query into a list of token-weight pairs, queries against a
    sparse vector field.

    :arg field: (required)The name of the field that contains the token-
        weight pairs to be searched against. This field must be a mapped
        sparse_vector field.
    :arg query_vector: Dictionary of precomputed sparse vectors and their
        associated weights. Only one of inference_id or query_vector may
        be supplied in a request.
    :arg inference_id: The inference ID to use to convert the query text
        into token-weight pairs. It must be the same inference ID that was
        used to create the tokens from the input text. Only one of
        inference_id and query_vector is allowed. If inference_id is
        specified, query must also be specified. Only one of inference_id
        or query_vector may be supplied in a request.
    :arg query: The query text you want to use for search. If inference_id
        is specified, query must also be specified.
    :arg prune: Whether to perform pruning, omitting the non-significant
        tokens from the query to improve query performance. If prune is
        true but the pruning_config is not specified, pruning will occur
        but default values will be used. Default: false
    :arg pruning_config: Optional pruning configuration. If enabled, this
        will omit non-significant tokens from the query in order to
        improve query performance. This is only used if prune is set to
        true. If prune is set to true but pruning_config is not specified,
        default values will be used.
    """

    name = "sparse_vector"

    def __init__(
        self,
        *,
        field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        query_vector: Union[Mapping[str, float], "NotSet"] = NOT_SET,
        inference_id: Union[str, "NotSet"] = NOT_SET,
        query: Union[str, "NotSet"] = NOT_SET,
        prune: Union[bool, "NotSet"] = NOT_SET,
        pruning_config: Union[
            "i.TokenPruningConfig", Dict[str, Any], "NotSet"
        ] = NOT_SET,
        **kwargs: Any,
    ):
        super().__init__(
            field=field,
            query_vector=query_vector,
            inference_id=inference_id,
            query=query,
            prune=prune,
            pruning_config=pruning_config,
            **kwargs,
        )


class Term(Query):
    """
    Returns documents that contain an exact term in a provided field. To
    return a document, the query term must exactly match the queried
    field's value, including whitespace and capitalization.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "term"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.TermQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class Terms(Query):
    """
    Returns documents that contain one or more exact terms in a provided
    field. To return a document, one or more terms must exactly match a
    field value, including whitespace and capitalization.
    """

    name = "terms"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _setattr(self, name: str, value: Any) -> None:
        # here we convert any iterables that are not strings to lists
        if hasattr(value, "__iter__") and not isinstance(value, (str, list)):
            value = list(value)
        super()._setattr(name, value)


class TermsSet(Query):
    """
    Returns documents that contain a minimum number of exact terms in a
    provided field. To return a document, a required number of terms must
    exactly match the field values, including whitespace and
    capitalization.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "terms_set"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.TermsSetQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class TextExpansion(Query):
    """
    Uses a natural language processing model to convert the query text
    into a list of token-weight pairs which are then used in a query
    against a sparse vector or rank features field.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "text_expansion"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.TextExpansionQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class WeightedTokens(Query):
    """
    Supports returning text_expansion query results by sending in
    precomputed tokens with the query.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "weighted_tokens"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.WeightedTokensQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class Wildcard(Query):
    """
    Returns documents that contain terms matching a wildcard pattern.

    :arg _field: The field to use in this query.
    :arg _value: The query value for the field.
    """

    name = "wildcard"

    def __init__(
        self,
        _field: Union[str, "InstrumentedField", "NotSet"] = NOT_SET,
        _value: Union["i.WildcardQuery", Dict[str, Any], "NotSet"] = NOT_SET,
        **kwargs: Any,
    ):
        if not isinstance(_field, NotSet):
            kwargs[str(_field)] = _value
        super().__init__(**kwargs)


class Wrapper(Query):
    """
    A query that accepts any other query as base64 encoded string.

    :arg query: (required)A base64 encoded query. The binary data format
        can be any of JSON, YAML, CBOR or SMILE encodings
    """

    name = "wrapper"

    def __init__(self, *, query: Union[str, "NotSet"] = NOT_SET, **kwargs: Any):
        super().__init__(query=query, **kwargs)


class Type(Query):
    """
    No documentation available.

    :arg value: (required)No documentation available.
    """

    name = "type"

    def __init__(self, *, value: Union[str, "NotSet"] = NOT_SET, **kwargs: Any):
        super().__init__(value=value, **kwargs)
