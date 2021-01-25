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

from datetime import datetime, timedelta

from .aggs import A
from .query import Nested, Range, Terms


class Facet(object):
    """
    A facet on faceted search. Wraps and aggregation and provides functionality
    to create a filter for selected values and return a list of facet values
    from the result of the aggregation.
    """

    agg_type = None

    def __init__(self, metric=None, metric_sort="desc", **kwargs):
        self.filter_values = ()
        self._params = kwargs
        self._metric = metric
        if metric and metric_sort:
            self._params["order"] = {"metric": metric_sort}

    def get_aggregation(self):
        """
        Return the aggregation object.
        """
        agg = A(self.agg_type, **self._params)
        if self._metric:
            agg.metric("metric", self._metric)
        return agg

    def add_filter(self, filter_values):
        """
        Construct a filter.
        """
        if not filter_values:
            return

        f = self.get_value_filter(filter_values[0])
        for v in filter_values[1:]:
            f |= self.get_value_filter(v)
        return f

    def get_value_filter(self, filter_value):
        """
        Construct a filter for an individual value
        """
        pass

    def is_filtered(self, key, filter_values):
        """
        Is a filter active on the given key.
        """
        return key in filter_values

    def get_value(self, bucket):
        """
        return a value representing a bucket. Its key as default.
        """
        return bucket["key"]

    def get_metric(self, bucket):
        """
        Return a metric, by default doc_count for a bucket.
        """
        if self._metric:
            return bucket["metric"]["value"]
        return bucket["doc_count"]

    def get_values(self, data, filter_values):
        """
        Turn the raw bucket data into a list of tuples containing the key,
        number of documents and a flag indicating whether this value has been
        selected or not.
        """
        out = []
        for bucket in data.buckets:
            key = self.get_value(bucket)
            out.append(
                (key, self.get_metric(bucket), self.is_filtered(key, filter_values))
            )
        return out


class TermsFacet(Facet):
    agg_type = "terms"

    def add_filter(self, filter_values):
        """ Create a terms filter instead of bool containing term filters.  """
        if filter_values:
            return Terms(
                _expand__to_dot=False, **{self._params["field"]: filter_values}
            )


class RangeFacet(Facet):
    agg_type = "range"

    def _range_to_dict(self, range):
        key, range = range
        out = {"key": key}
        if range[0] is not None:
            out["from"] = range[0]
        if range[1] is not None:
            out["to"] = range[1]
        return out

    def __init__(self, ranges, **kwargs):
        super(RangeFacet, self).__init__(**kwargs)
        self._params["ranges"] = list(map(self._range_to_dict, ranges))
        self._params["keyed"] = False
        self._ranges = dict(ranges)

    def get_value_filter(self, filter_value):
        f, t = self._ranges[filter_value]
        limits = {}
        if f is not None:
            limits["gte"] = f
        if t is not None:
            limits["lt"] = t

        return Range(_expand__to_dot=False, **{self._params["field"]: limits})


class HistogramFacet(Facet):
    agg_type = "histogram"

    def get_value_filter(self, filter_value):
        return Range(
            _expand__to_dot=False,
            **{
                self._params["field"]: {
                    "gte": filter_value,
                    "lt": filter_value + self._params["interval"],
                }
            }
        )


def _date_interval_month(d):
    return (d + timedelta(days=32)).replace(day=1)


def _date_interval_week(d):
    return d + timedelta(days=7)


def _date_interval_day(d):
    return d + timedelta(days=1)


def _date_interval_hour(d):
    return d + timedelta(hours=1)


class DateHistogramFacet(Facet):
    agg_type = "date_histogram"

    DATE_INTERVALS = {
        "month": _date_interval_month,
        "1M": _date_interval_month,
        "week": _date_interval_week,
        "1w": _date_interval_week,
        "day": _date_interval_day,
        "1d": _date_interval_day,
        "hour": _date_interval_hour,
        "1h": _date_interval_hour,
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("min_doc_count", 0)
        super(DateHistogramFacet, self).__init__(**kwargs)

    def get_value(self, bucket):
        if not isinstance(bucket["key"], datetime):
            # Elasticsearch returns key=None instead of 0 for date 1970-01-01,
            # so we need to set key to 0 to avoid TypeError exception
            if bucket["key"] is None:
                bucket["key"] = 0
            # Preserve milliseconds in the datetime
            return datetime.utcfromtimestamp(int(bucket["key"]) / 1000.0)
        else:
            return bucket["key"]

    def get_value_filter(self, filter_value):
        for interval_type in ("calendar_interval", "fixed_interval"):
            if interval_type in self._params:
                break
        else:
            interval_type = "interval"

        return Range(
            _expand__to_dot=False,
            **{
                self._params["field"]: {
                    "gte": filter_value,
                    "lt": self.DATE_INTERVALS[self._params[interval_type]](
                        filter_value
                    ),
                }
            }
        )


class NestedFacet(Facet):
    agg_type = "nested"

    def __init__(self, path, nested_facet):
        self._path = path
        self._inner = nested_facet
        super(NestedFacet, self).__init__(
            path=path, aggs={"inner": nested_facet.get_aggregation()}
        )

    def get_values(self, data, filter_values):
        return self._inner.get_values(data.inner, filter_values)

    def add_filter(self, filter_values):
        inner_q = self._inner.add_filter(filter_values)
        if inner_q:
            return Nested(path=self._path, query=inner_q)


from ._base.faceted_search import FacetedResponse
from ._sync.faceted_search import FacetedSearch

__all__ = [
    "FacetedSearch",
    "FacetedResponse",
    "HistogramFacet",
    "TermsFacet",
    "DateHistogramFacet",
    "RangeFacet",
    "NestedFacet",
]

try:
    from ._async.faceted_search import AsyncFacetedSearch  # noqa: F401

    __all__.append("AsyncFacetedSearch")
except (ImportError, SyntaxError):
    pass
