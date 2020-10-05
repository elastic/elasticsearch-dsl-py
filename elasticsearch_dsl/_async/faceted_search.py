from elasticsearch_dsl.faceted_search import FacetedSearch


class AsyncFacetedSearch(FacetedSearch):
    async def execute(self):
        """
        Asynchronously execute the search and return the response.
        """
        r = await self._s.execute()
        r._faceted_search = self
        return r
