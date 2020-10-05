from elasticsearch import AsyncElasticsearch
from elasticsearch._async.helpers import async_scan

from elasticsearch_dsl._async.utils import ensure_async_connection
from elasticsearch_dsl.connections import get_connection
from elasticsearch_dsl.search import MultiSearch, Search
from elasticsearch_dsl.utils import AttrDict


class AsyncMultiSearch(MultiSearch):
    async def execute(self, ignore_cache=False, raise_on_error=True):
        """
        Execute the multi search request and return a list of search results.
        """
        if ignore_cache or not hasattr(self, "_response"):
            es = get_connection(self._using)
            ensure_async_connection(es, "AsyncMultiSearch.execute")

            responses = await es.msearch(
                index=self._index,
                body=self.to_dict(),
                **self.params,
            )

            self._response = self._process_responses(
                responses, raise_on_error=raise_on_error
            )

        return self._response


class AsyncSearch(Search):
    async def __aiter__(self):
        """
        Asynchronously iterates over the hits.
        """
        return iter(self.execute())

    async def execute(self, ignore_cache=False):
        if ignore_cache or not hasattr(self, "_response"):
            es = get_connection(self._using)
            ensure_async_connection(es, "AsyncSearch.execute")

            self._response = self._response_class(
                self,
                await es.search(index=self._index, body=self.to_dict(), **self._params),
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
        ensure_async_connection(es, "AsyncSearch.scan")

        for hit in await async_scan(
            es, query=self.to_dict(), index=self._index, **self._params
        ):
            yield self._get_result(hit)

    async def delete(self):
        """
        delete() executes the query by delegating to delete_by_query()
        """
        es = get_connection(self._using)
        ensure_async_connection(es, "AsyncSearch.delete")

        return AttrDict(
            await es.delete_by_query(
                index=self._index, body=self.to_dict(), **self._params
            )
        )
