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

import asyncio
import os

from elasticsearch_dsl import (
    AsyncDocument,
    AsyncSearch,
    Keyword,
    Percolator,
    Q,
    Text,
    async_connections,
)


class BlogPost(AsyncDocument):
    """
    Blog posts that will be automatically tagged based on percolation queries.
    """

    content = Text()
    tags = Keyword(multi=True)

    class Index:
        name = "test-blogpost"

    async def add_tags(self):
        # run a percolation to automatically tag the blog post.
        s = AsyncSearch(index="test-percolator")
        s = s.query(
            "percolate", field="query", index=self._get_index(), document=self.to_dict()
        )

        # collect all the tags from matched percolators
        async for percolator in s:
            self.tags.extend(percolator.tags)

        # make sure tags are unique
        self.tags = list(set(self.tags))

    async def save(self, **kwargs):
        await self.add_tags()
        return await super().save(**kwargs)


class PercolatorDoc(AsyncDocument):
    """
    Document class used for storing the percolation queries.
    """

    # relevant fields from BlogPost must be also present here for the queries
    # to be able to use them. Another option would be to use document
    # inheritance but save() would have to be reset to normal behavior.
    content = Text()

    # the percolator query to be run against the doc
    query = Percolator()
    # list of tags to append to a document
    tags = Keyword(multi=True)

    class Index:
        name = "test-percolator"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}


async def setup():
    # create the percolator index if it doesn't exist
    if not await PercolatorDoc._index.exists():
        await PercolatorDoc.init()

    # register a percolation query looking for documents about python
    await PercolatorDoc(
        _id="python",
        tags=["programming", "development", "python"],
        query=Q("match", content="python"),
    ).save(refresh=True)


async def main():
    # initiate the default connection to elasticsearch
    async_connections.create_connection(hosts=[os.environ["ELASTICSEARCH_URL"]])

    await setup()

    # close the connection
    await async_connections.get_connection().close()


if __name__ == "__main__":
    asyncio.run(main())
