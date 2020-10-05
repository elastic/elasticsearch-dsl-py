from elasticsearch import AsyncElasticsearch

from elasticsearch_dsl._async.utils import ensure_async_connection
from elasticsearch_dsl.connections import get_connection
from elasticsearch_dsl.update_by_query import UpdateByQuery


class AsyncUpdateByQuery(UpdateByQuery):
    async def execute(self):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.
        """
        es = get_connection(self._using)
        ensure_async_connection(es, "AsyncMultiSearch.execute")

        self._response = self._response_class(
            self,
            await es.update_by_query(
                index=self._index, body=self.to_dict(), **self._params
            ),
        )
        return self._response
