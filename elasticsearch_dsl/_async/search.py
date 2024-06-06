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

from elasticsearch.exceptions import ApiError
from elasticsearch.helpers import async_scan

from ..async_connections import get_connection
from ..response import Response
from ..search_base import MultiSearchBase, SearchBase
from ..utils import AttrDict


class AsyncSearch(SearchBase):
    def __aiter__(self):
        """
        Iterate over the hits.
        """

        class ResultsIterator:
            def __init__(self, search):
                self.search = search
                self.iterator = None

            async def __anext__(self):
                if self.iterator is None:
                    self.iterator = iter(await self.search.execute())
                try:
                    return next(self.iterator)
                except StopIteration:
                    raise StopAsyncIteration()

        return ResultsIterator(self)

    async def count(self):
        """
        Return the number of hits matching the query and filters. Note that
        only the actual number is returned.
        """
        if hasattr(self, "_response") and self._response.hits.total.relation == "eq":
            return self._response.hits.total.value

        es = get_connection(self._using)

        d = self.to_dict(count=True)
        # TODO: failed shards detection
        resp = await es.count(
            index=self._index, query=d.get("query", None), **self._params
        )
        return resp["count"]

    async def execute(self, ignore_cache=False):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.

        :arg ignore_cache: if set to ``True``, consecutive calls will hit
            ES, while cached result will be ignored. Defaults to `False`
        """
        if ignore_cache or not hasattr(self, "_response"):
            es = get_connection(self._using)

            self._response = self._response_class(
                self,
                (
                    await es.search(
                        index=self._index, body=self.to_dict(), **self._params
                    )
                ).body,
            )
        return self._response

    async def scan(self):
        """
        Turn the search into a scan search and return a generator that will
        iterate over all the documents matching the query.

        Use ``params`` method to specify any additional arguments you with to
        pass to the underlying ``scan`` helper from ``elasticsearch-py`` -
        https://elasticsearch-py.readthedocs.io/en/master/helpers.html#elasticsearch.helpers.scan

        """
        es = get_connection(self._using)

        async for hit in async_scan(
            es, query=self.to_dict(), index=self._index, **self._params
        ):
            yield self._get_result(hit)

    async def delete(self):
        """
        delete() executes the query by delegating to delete_by_query()
        """

        es = get_connection(self._using)

        return AttrDict(
            await es.delete_by_query(
                index=self._index, body=self.to_dict(), **self._params
            )
        )


class AsyncMultiSearch(MultiSearchBase):
    """
    Combine multiple :class:`~elasticsearch_dsl.Search` objects into a single
    request.
    """

    async def execute(self, ignore_cache=False, raise_on_error=True):
        """
        Execute the multi search request and return a list of search results.
        """
        if ignore_cache or not hasattr(self, "_response"):
            es = get_connection(self._using)

            responses = await es.msearch(
                index=self._index, body=self.to_dict(), **self._params
            )

            out = []
            for s, r in zip(self._searches, responses["responses"]):
                if r.get("error", False):
                    if raise_on_error:
                        raise ApiError("N/A", meta=responses.meta, body=r)
                    r = None
                else:
                    r = Response(s, r)
                out.append(r)

            self._response = out

        return self._response


class AsyncEmptySearch(AsyncSearch):
    async def count(self):
        return 0

    async def execute(self, ignore_cache=False):
        return self._response_class(self, {"hits": {"total": 0, "hits": []}})

    async def scan(self):
        return
        yield  # a bit strange, but this forces an empty generator function

    async def delete(self):
        return AttrDict({})
