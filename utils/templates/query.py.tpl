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
from .utils import DslBase, NotSet, NOT_SET

if TYPE_CHECKING:
    from .document_base import InstrumentedField
    from elasticsearch_dsl import interfaces as i, wrappers

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


{% include "dsl_classes.tpl" %}
