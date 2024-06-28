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
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    MutableMapping,
    Optional,
    Union,
    cast,
)

from typing_extensions import TypeVar

from .response import Hit
from .response.aggs import AggResponse, BucketData, FieldBucketData, TopHitsData
from .utils import AttrDict, DslBase, JSONType

if TYPE_CHECKING:
    from .query import Query
    from .search_base import SearchBase

_R = TypeVar("_R", default=Hit)


def A(
    name_or_agg: Union[MutableMapping[str, Any], "Agg[_R]", str],
    filter: Optional[Union[str, "Query"]] = None,
    **params: Any,
) -> "Agg[_R]":
    if filter is not None:
        if name_or_agg != "filter":
            raise ValueError(
                "Aggregation %r doesn't accept positional argument 'filter'."
                % name_or_agg
            )
        params["filter"] = filter

    # {"terms": {"field": "tags"}, "aggs": {...}}
    if isinstance(name_or_agg, collections.abc.MutableMapping):
        if params:
            raise ValueError("A() cannot accept parameters when passing in a dict.")
        # copy to avoid modifying in-place
        agg = deepcopy(name_or_agg)
        # pop out nested aggs
        aggs = agg.pop("aggs", None)
        # pop out meta data
        meta = agg.pop("meta", None)
        # should be {"terms": {"field": "tags"}}
        if len(agg) != 1:
            raise ValueError(
                'A() can only accept dict with an aggregation ({"terms": {...}}). '
                "Instead it got (%r)" % name_or_agg
            )
        agg_type, params = agg.popitem()
        if aggs:
            params = params.copy()
            params["aggs"] = aggs
        if meta:
            params = params.copy()
            params["meta"] = meta
        return Agg[_R].get_dsl_class(agg_type)(_expand__to_dot=False, **params)

    # Terms(...) just return the nested agg
    elif isinstance(name_or_agg, Agg):
        if params:
            raise ValueError(
                "A() cannot accept parameters when passing in an Agg object."
            )
        return name_or_agg

    # "terms", field="tags"
    return Agg[_R].get_dsl_class(name_or_agg)(**params)


class Agg(DslBase, Generic[_R]):
    _type_name = "agg"
    _type_shortcut = staticmethod(A)
    name = ""

    def __contains__(self, key: str) -> bool:
        return False

    def to_dict(self) -> Dict[str, JSONType]:
        d = super().to_dict()
        if isinstance(d[self.name], dict):
            n = cast(Dict[str, JSONType], d[self.name])
            if "meta" in n:
                d["meta"] = n.pop("meta")
        return d

    def result(self, search: "SearchBase[_R]", data: Dict[str, Any]) -> AttrDict[Any]:
        return AggResponse[_R](self, search, data)


class AggBase(Generic[_R]):
    aggs: Dict[str, Agg[_R]]
    _base: Agg[_R]
    _params: Dict[str, Any]
    _param_defs: ClassVar[Dict[str, Any]] = {
        "aggs": {"type": "agg", "hash": True},
    }

    def __contains__(self, key: str) -> bool:
        return key in self._params.get("aggs", {})

    def __getitem__(self, agg_name: str) -> Agg[_R]:
        agg = cast(
            Agg[_R], self._params.setdefault("aggs", {})[agg_name]
        )  # propagate KeyError

        # make sure we're not mutating a shared state - whenever accessing a
        # bucket, return a shallow copy of it to be safe
        if isinstance(agg, Bucket):
            agg = A(agg.name, filter=None, **agg._params)
            # be sure to store the copy so any modifications to it will affect us
            self._params["aggs"][agg_name] = agg

        return agg

    def __setitem__(self, agg_name: str, agg: Agg[_R]) -> None:
        self.aggs[agg_name] = A(agg)

    def __iter__(self) -> Iterable[str]:
        return iter(self.aggs)

    def _agg(
        self, bucket: bool, name: str, agg_type: str, *args: Any, **params: Any
    ) -> Agg[_R]:
        agg = self[name] = A(agg_type, *args, **params)

        # For chaining - when creating new buckets return them...
        if bucket:
            return agg
        # otherwise return self._base so we can keep chaining
        else:
            return self._base

    def metric(self, name: str, agg_type: str, *args: Any, **params: Any) -> Agg[_R]:
        return self._agg(False, name, agg_type, *args, **params)

    def bucket(self, name: str, agg_type: str, *args: Any, **params: Any) -> Agg[_R]:
        return self._agg(True, name, agg_type, *args, **params)

    def pipeline(self, name: str, agg_type: str, *args: Any, **params: Any) -> Agg[_R]:
        return self._agg(False, name, agg_type, *args, **params)

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return BucketData(self, search, data)  # type: ignore


class Bucket(AggBase[_R], Agg[_R]):
    def __init__(self, **params: Any):
        super().__init__(**params)
        # remember self for chaining
        self._base = self

    def to_dict(self) -> Dict[str, JSONType]:
        d = super(AggBase, self).to_dict()
        if isinstance(d[self.name], dict):
            n = cast(AttrDict[Any], d[self.name])
            if "aggs" in n:
                d["aggs"] = n.pop("aggs")
        return d


class Filter(Bucket[_R]):
    name = "filter"
    _param_defs = {
        "filter": {"type": "query"},
        "aggs": {"type": "agg", "hash": True},
    }

    def __init__(self, filter: Optional[Union[str, "Query"]] = None, **params: Any):
        if filter is not None:
            params["filter"] = filter
        super().__init__(**params)

    def to_dict(self) -> Dict[str, JSONType]:
        d = super().to_dict()
        if isinstance(d[self.name], dict):
            n = cast(AttrDict[Any], d[self.name])
            n.update(n.pop("filter", {}))
        return d


class Pipeline(Agg[_R]):
    pass


# bucket aggregations
class Filters(Bucket[_R]):
    name = "filters"
    _param_defs = {
        "filters": {"type": "query", "hash": True},
        "aggs": {"type": "agg", "hash": True},
    }


class Children(Bucket[_R]):
    name = "children"


class Parent(Bucket[_R]):
    name = "parent"


class DateHistogram(Bucket[_R]):
    name = "date_histogram"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return FieldBucketData(self, search, data)


class AutoDateHistogram(DateHistogram[_R]):
    name = "auto_date_histogram"


class AdjacencyMatrix(Bucket[_R]):
    name = "adjacency_matrix"


class DateRange(Bucket[_R]):
    name = "date_range"


class GeoDistance(Bucket[_R]):
    name = "geo_distance"


class GeohashGrid(Bucket[_R]):
    name = "geohash_grid"


class GeohexGrid(Bucket[_R]):
    name = "geohex_grid"


class GeotileGrid(Bucket[_R]):
    name = "geotile_grid"


class GeoCentroid(Bucket[_R]):
    name = "geo_centroid"


class Global(Bucket[_R]):
    name = "global"


class Histogram(Bucket[_R]):
    name = "histogram"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return FieldBucketData(self, search, data)


class IPRange(Bucket[_R]):
    name = "ip_range"


class IPPrefix(Bucket[_R]):
    name = "ip_prefix"


class Missing(Bucket[_R]):
    name = "missing"


class Nested(Bucket[_R]):
    name = "nested"


class Range(Bucket[_R]):
    name = "range"


class RareTerms(Bucket[_R]):
    name = "rare_terms"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return FieldBucketData(self, search, data)


class ReverseNested(Bucket[_R]):
    name = "reverse_nested"


class SignificantTerms(Bucket[_R]):
    name = "significant_terms"


class SignificantText(Bucket[_R]):
    name = "significant_text"


class Terms(Bucket[_R]):
    name = "terms"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return FieldBucketData(self, search, data)


class Sampler(Bucket[_R]):
    name = "sampler"


class DiversifiedSampler(Bucket[_R]):
    name = "diversified_sampler"


class RandomSampler(Bucket[_R]):
    name = "random_sampler"


class Composite(Bucket[_R]):
    name = "composite"
    _param_defs = {
        "sources": {"type": "agg", "hash": True, "multi": True},
        "aggs": {"type": "agg", "hash": True},
    }


class VariableWidthHistogram(Bucket[_R]):
    name = "variable_width_histogram"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return FieldBucketData(self, search, data)


class MultiTerms(Bucket[_R]):
    name = "multi_terms"


class CategorizeText(Bucket[_R]):
    name = "categorize_text"


# metric aggregations
class TopHits(Agg[_R]):
    name = "top_hits"

    def result(self, search: "SearchBase[_R]", data: Any) -> AttrDict[Any]:
        return TopHitsData(self, search, data)


class Avg(Agg[_R]):
    name = "avg"


class WeightedAvg(Agg[_R]):
    name = "weighted_avg"


class Cardinality(Agg[_R]):
    name = "cardinality"


class ExtendedStats(Agg[_R]):
    name = "extended_stats"


class Boxplot(Agg[_R]):
    name = "boxplot"


class GeoBounds(Agg[_R]):
    name = "geo_bounds"


class GeoLine(Agg[_R]):
    name = "geo_line"


class Max(Agg[_R]):
    name = "max"


class MatrixStats(Agg[_R]):
    name = "matrix_stats"


class MedianAbsoluteDeviation(Agg[_R]):
    name = "median_absolute_deviation"


class Min(Agg[_R]):
    name = "min"


class Percentiles(Agg[_R]):
    name = "percentiles"


class PercentileRanks(Agg[_R]):
    name = "percentile_ranks"


class ScriptedMetric(Agg[_R]):
    name = "scripted_metric"


class Stats(Agg[_R]):
    name = "stats"


class Sum(Agg[_R]):
    name = "sum"


class TopMetrics(Agg[_R]):
    name = "top_metrics"


class TTest(Agg[_R]):
    name = "t_test"


class ValueCount(Agg[_R]):
    name = "value_count"


# pipeline aggregations
class AvgBucket(Pipeline[_R]):
    name = "avg_bucket"


class BucketScript(Pipeline[_R]):
    name = "bucket_script"


class BucketSelector(Pipeline[_R]):
    name = "bucket_selector"


class CumulativeSum(Pipeline[_R]):
    name = "cumulative_sum"


class CumulativeCardinality(Pipeline[_R]):
    name = "cumulative_cardinality"


class Derivative(Pipeline[_R]):
    name = "derivative"


class ExtendedStatsBucket(Pipeline[_R]):
    name = "extended_stats_bucket"


class Inference(Pipeline[_R]):
    name = "inference"


class MaxBucket(Pipeline[_R]):
    name = "max_bucket"


class MinBucket(Pipeline[_R]):
    name = "min_bucket"


class MovingFn(Pipeline[_R]):
    name = "moving_fn"


class MovingAvg(Pipeline[_R]):
    name = "moving_avg"


class MovingPercentiles(Pipeline[_R]):
    name = "moving_percentiles"


class Normalize(Pipeline[_R]):
    name = "normalize"


class PercentilesBucket(Pipeline[_R]):
    name = "percentiles_bucket"


class SerialDiff(Pipeline[_R]):
    name = "serial_diff"


class StatsBucket(Pipeline[_R]):
    name = "stats_bucket"


class SumBucket(Pipeline[_R]):
    name = "sum_bucket"


class BucketSort(Pipeline[_R]):
    name = "bucket_sort"
