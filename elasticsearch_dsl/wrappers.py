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

import operator
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Literal,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import TypeAlias

from .utils import AttrDict


class SupportsDunderLT(Protocol):
    def __lt__(self, other: Any, /) -> Any: ...


class SupportsDunderGT(Protocol):
    def __gt__(self, other: Any, /) -> Any: ...


class SupportsDunderLE(Protocol):
    def __le__(self, other: Any, /) -> Any: ...


class SupportsDunderGE(Protocol):
    def __ge__(self, other: Any, /) -> Any: ...


SupportsComparison: TypeAlias = Union[
    SupportsDunderLE, SupportsDunderGE, SupportsDunderGT, SupportsDunderLT
]

ComparisonOperators: TypeAlias = Literal["lt", "lte", "gt", "gte"]
RangeValT = TypeVar("RangeValT", bound=SupportsComparison)

__all__ = ["Range", "SupportsComparison"]


class Range(AttrDict[ComparisonOperators, RangeValT]):
    OPS: ClassVar[
        Mapping[
            ComparisonOperators,
            Callable[[SupportsComparison, SupportsComparison], bool],
        ]
    ] = {
        "lt": operator.lt,
        "lte": operator.le,
        "gt": operator.gt,
        "gte": operator.ge,
    }

    def __init__(
        self,
        d: Optional[Dict[ComparisonOperators, RangeValT]] = None,
        /,
        **kwargs: RangeValT,
    ):
        if d is not None and (kwargs or not isinstance(d, dict)):
            raise ValueError(
                "Range accepts a single dictionary or a set of keyword arguments."
            )

        # Cast here since mypy is inferring d as an `object` type for some reason
        data = cast(Dict[str, RangeValT], d) if d is not None else kwargs

        for k in data:
            if k not in self.OPS:
                raise ValueError(f"Range received an unknown operator {k!r}")

        if "gt" in data and "gte" in data:
            raise ValueError("You cannot specify both gt and gte for Range.")

        if "lt" in data and "lte" in data:
            raise ValueError("You cannot specify both lt and lte for Range.")

        # Here we use cast() since we now the keys are in the allowed values, but mypy does
        # not infer it.
        super().__init__(cast(Dict[ComparisonOperators, RangeValT], data))

    def __repr__(self) -> str:
        return "Range(%s)" % ", ".join("%s=%r" % op for op in self._d_.items())

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return super().__contains__(item)

        item_supports_comp = any(hasattr(item, f"__{op}__") for op in self.OPS)
        if not item_supports_comp:
            return False

        # Cast to tell mypy whe have checked it and its ok to use the comparison methods
        # on `item`
        item = cast(SupportsComparison, item)

        for op in self.OPS:
            if op in self._d_ and not self.OPS[op](item, self._d_[op]):
                return False
        return True

    @property
    def upper(self) -> Union[Tuple[RangeValT, bool], Tuple[None, Literal[False]]]:
        if "lt" in self._d_:
            return self._d_["lt"], False
        if "lte" in self._d_:
            return self._d_["lte"], True
        return None, False

    @property
    def lower(self) -> Union[Tuple[RangeValT, bool], Tuple[None, Literal[False]]]:
        if "gt" in self._d_:
            return self._d_["gt"], False
        if "gte" in self._d_:
            return self._d_["gte"], True
        return None, False
