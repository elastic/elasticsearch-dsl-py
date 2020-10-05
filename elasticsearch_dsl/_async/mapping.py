from elasticsearch_dsl._async.utils import ensure_async_connection
from elasticsearch_dsl.connections import get_connection
from elasticsearch_dsl.mapping import Mapping


class AsyncMapping(Mapping):
    @classmethod
    async def from_es(cls, index, using="default"):
        m = cls()
        await m.update_from_es(index, using)

        return m

    async def save(self, index, using="default"):
        from elasticsearch_dsl._async.index import AsyncIndex

        index = AsyncIndex(index, using=using)
        index.mapping(self)
        return await index.save()

    async def update_from_es(self, index, using="default"):
        es = get_connection(using)
        ensure_async_connection(es, "AsyncMapping.update_from_es")

        raw = await es.indices.get_mapping(index=index)
        _, raw = raw.popitem()
        self._update_from_dict(raw["mappings"])
