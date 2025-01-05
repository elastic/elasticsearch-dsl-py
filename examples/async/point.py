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

"""
Example ``Document`` with point datatype.

In the ``Place`` class we index the place's location as coordinates
to allow spatial queries and distance-based searches.
"""

import asyncio
import os
from typing import TYPE_CHECKING, Any, Optional

import elasticsearch_dsl as dsl


class Place(dsl.AsyncDocument):
    if TYPE_CHECKING:
        # definitions here help type checkers understand additional arguments
        # that are allowed in the constructor
        _id: Optional[int] = dsl.mapped_field(default=None)

    location: Any = dsl.mapped_field(dsl.Point(), default="")

    class Index:
        name = "test-point"


async def main() -> None:
    # initiate the default connection to elasticsearch
    dsl.async_connections.create_connection(hosts=[os.environ["ELASTICSEARCH_URL"]])

    # create the empty index
    await Place.init()

    # index some sample data
    for id, location in enumerate(
        [
            {"type": "Point", "coordinates": [5.43, 32.11]},
            "POINT (-71.34 41.12)",
            {"x": -75.22, "y": -3.14},
            [19.12, 52],
            "84.12,-54.24",
        ],
    ):
        await Place(_id=id, location=location).save()

    # refresh index manually to make changes live
    await Place._index.refresh()

    # close the connection
    await dsl.async_connections.get_connection().close()


if __name__ == "__main__":
    asyncio.run(main())
