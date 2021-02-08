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

META_FIELDS = frozenset(
    (
        "dynamic",
        "transform",
        "dynamic_date_formats",
        "date_detection",
        "numeric_detection",
        "dynamic_templates",
        "enabled",
    )
)

__all__ = [
    "Properties",
    "Mapping",
    "META_FIELDS",
]

from ._base.mapping import Properties
from ._sync.mapping import Mapping

try:
    from ._async.mapping import AsyncMapping  # noqa: F401

    __all__.append("AsyncMapping")
except (ImportError, SyntaxError):
    pass
