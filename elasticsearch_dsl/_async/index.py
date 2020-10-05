from elasticsearch import AsyncElasticsearch

from elasticsearch_dsl._async.utils import ensure_async_connection
from elasticsearch_dsl.connections import get_connection
from elasticsearch_dsl.index import Index, IndexTemplate


class AsyncIndex(Index):
    async def analyze(self, using=None, **kwargs):
        """
        Asynchronously perform the analysis process on a text and return the tokens
        breakdown of the text.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.analyze`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.analyze")

        return await es.indices.analyze(index=self._index, **kwargs)

    async def clear_cache(self, using=None, **kwargs):
        """
        Asynchronously clear all caches or specific cached associated with the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.clear_cache`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.clear_cache")

        return await es.indices.clear_cache(index=self._index, **kwargs)

    async def close(self, using=None, **kwargs):
        """
        Asynchronously closes the index in Elasticsearch.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.close`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.close")

        return await es.indices.close(index=self._index, **kwargs)

    async def create(self, using=None, **kwargs):
        """
        Asynchronously creates the index in Elasticsearch.

        Any additional keyword arguments will be passed to
        ``Elasticsearch.indices.create`` unchanged.
        """
        es = get_connection(using)
        ensure_async_connection(es, "AsyncIndex.create")

        return await es.indices.create(
            index=self._name,
            body=self.to_dict(),
            **kwargs,
        )

    async def delete(self, using=None, **kwargs):
        """
        Asynchronously deletes the index in Elasticsearch.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.delete`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.delete")

        return await es.indices.delete(index=self._index, **kwargs)

    async def delete_alias(self, using=None, **kwargs):
        """
        Asynchronously deletes a specific alias.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.delete_alias`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.delete_alias")

        return await es.indices.delete_alias(index=self._index, **kwargs)

    async def exists(self, using=None, **kwargs):
        """
        Asynchronously queries Elasticsearch for whether this index exists. Returns
        ``True`` if the index already exists in Elasticsearch, otherwise ``False``.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.exists`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.exists")

        return await es.indices.exists(index=self._index, **kwargs)

    async def exists_type(self, using=None, **kwargs):
        """
        Asynchronously queries Elasticsearch for whether a type or set of types exists
        in the index. Returns ``True`` if the type/types exist, otherwise ``False``.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.exists_type`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.exists_type")

        return await es.indices.exists_type(index=self._index, **kwargs)

    async def flush(self, using=None, **kwargs):
        """
        Asynchronously performs a flush operation on the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.flush`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.flush")

        return await es.indices.flush(index=self._index, **kwargs)

    async def flush_synced(self, using=None, **kwargs):
        """
        Asynchronously performs a normal flush, then adds a unique marker (sync_id) to
        all shards.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.flush_synced`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.flush_synced")

        return await es.indices.flush_synced(index=self._index, **kwargs)

    async def forcemerge(self, using=None, **kwargs):
        """
        Asynchronously calls the force merge API.

        The force merge API allows to force merging of the index through an API. The
        merge relates to the number of segments a Lucene index holds within each shard.
        The force merge operation allows to reduce the number of segments by merging
        them.

        This call will block until the merge is complete. If the http connection is
        lost, the request will continue in the background, and any new requests will
        block until the previous force merge is complete.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.forcemerge`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.forcemerge")

        return await es.indices.forcemerge(index=self._index, **kwargs)

    async def get(self, using=None, **kwargs):
        """
        Asynchronously retrieves information about the index from Elasticsearch.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get")

        return await es.indices.get(index=self._index, **kwargs)

    async def get_alias(self, using=None, **kwargs):
        """
        Asynchronously retrieves a specific alias.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get_alias`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get_alias")

        return await es.indices.get_alias(index=self._index, **kwargs)

    async def get_field_mapping(self, using=None, **kwargs):
        """
        Asynchronously retrieves a mapping definition for a specific field.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get_field_mapping`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get_field_mapping")

        return await es.indices.get_field_mapping(index=self._index, **kwargs)

    async def get_mapping(self, using=None, **kwargs):
        """
        Asynchronously retrieves a specific mapping definition for a specific type.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get_mapping`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get_mapping")

        return await es.indices.get_mapping(index=self._index, **kwargs)

    async def get_settings(self, using=None, **kwargs):
        """
        Asynchronously retrieves the settings for the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get_settings`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get_settings")

        return await es.indices.get_settings(index=self._index, **kwargs)

    async def get_upgrade(self, using=None, **kwargs):
        """
        Asynchronously monitors how much of an index is upgraded.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.get_upgrade`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.get_upgrade")

        return await es.indices.get_upgrade(index=self._index, **kwargs)

    async def is_closed(self, using=None):
        """
        Asynchronously queries Elasticsearch to determine whether this index
        is closed.
        """
        es = get_connection(using)
        ensure_async_connection(es, "AsyncIndex.is_closed")

        state = await es.cluster.state(
            index=self._name,
            metric="metadata",
        )

        return state["metadata"]["indices"][self._name]["state"] == "close"

    async def load_mappings(self, using=None):
        mapping = self.get_or_create_mapping()

        await mapping.update_from_es(self._name, using=using or self._using)

    async def open(self, using=None, **kwargs):
        """
        Asynchronously opens the index in Elasticsearch.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.open`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.open")

        return await es.indices.open(index=self._index, **kwargs)

    async def put_alias(self, using=None, **kwargs):
        """
        Asynchronously creates an alias for the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.put_alias`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.put_alias")

        return await es.indices.put_alias(index=self._index, **kwargs)

    async def put_mapping(self, using=None, **kwargs):
        """
        Asynchronously register a specific mapping definition for a specific type.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.put_mapping`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.put_mapping")

        return await es.indices.put_mapping(index=self._index, **kwargs)

    async def put_settings(self, using=None, **kwargs):
        """
        Asynchronously changes specific index-level settings.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.put_settings`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.put_settings")

        return await es.indices.put_settings(index=self._index, **kwargs)

    async def recovery(self, using=None, **kwargs):
        """
        Asynchronously provides insight into ongoing shard recoveries for the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.recovery`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.recovery")

        return await es.indices.recovery(index=self._index, **kwargs)

    async def refresh(self, using=None, **kwargs):
        """
        Asynchronously performs a refresh operation on the index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.refresh`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.refresh")

        return await es.indices.refresh(index=self._index, **kwargs)

    async def save(self, using=None):
        """
        Asynchronously sync the index definition with Elasticsearch, creating the index
        if it doesn't exist and updating its settings and mappings if it does.

        Note: Some settings and mapping changes cannot be done on an open index (or at
        all on an existing index) and for those this method will fail with the
        underlying exception.
        """

        if not await self.exists(using=using):
            return await self.create(using=using)

        body = self.to_dict()
        settings = body.pop("settings", {})
        analysis = settings.pop("analysis", None)
        current_settings = self.get_settings(using=using)[self._name]["settings"][
            "index"
        ]

        if analysis:
            if await self.is_closed(using=using):
                # closed index, update away
                settings["analysis"] = analysis
            else:
                # compare analysis definition, if all analysis objects are
                # already defined as requested, skip analysis update and
                # proceed, otherwise raise IllegalOperation
                existing_analysis = current_settings.get("analysis", {})
                if any(
                    existing_analysis.get(section, {}).get(k, None)
                    != analysis[section][k]
                    for section in analysis
                    for k in analysis[section]
                ):
                    raise IllegalOperation(
                        "You cannot update analysis configuration on an open index, "
                        "you need to close index %s first." % self._name
                    )

        # try and update the settings
        if settings:
            settings = settings.copy()
            for k, v in list(settings.items()):
                if k in current_settings and current_settings[k] == str(v):
                    del settings[k]

            if settings:
                await self.put_settings(using=using, body=settings)

        # update the mappings, any conflict in the mappings will result in an
        # exception
        mappings = body.pop("mappings", {})
        if mappings:
            await self.put_mapping(using=using, body=mappings)

    async def segments(self, using=None, **kwargs):
        """
        Asynchronously provides low-level segments information that a Lucene index
        (shard level) is built with.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.segments`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.segments")

        return await es.indices.segments(index=self._index, **kwargs)

    async def shard_stores(self, using=None, **kwargs):
        """
        Asynchronously provides store information for shard copies of the index. Store
        information reports on which nodes shard copies exist, the shard copy version,
        indicating how recent they are, and any exceptions encountered while opening
        the shard index or from earlier engine failure.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.shard_stores`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.shard_stores")

        return await es.indices.shard_stores(index=self._index, **kwargs)

    async def shrink(self, using=None, **kwargs):
        """
        Asynchronously calls the shrink index API.

        The shrink index API allows you to shrink an existing index into a new
        index with fewer primary shards. The number of primary shards in the
        target index must be a factor of the shards in the source index. For
        example an index with 8 primary shards can be shrunk into 4, 2 or 1
        primary shards or an index with 15 primary shards can be shrunk into 5,
        3 or 1. If the number of shards in the index is a prime number it can
        only be shrunk into a single primary shard. Before shrinking, a
        (primary or replica) copy of every shard in the index must be present
        on the same node.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.shrink`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.shrink")

        return await es.indices.shrink(index=self._index, **kwargs)

    async def stats(self, using=None, **kwargs):
        """
        Asynchronously retrieves statistics on different operations happening on the
        index.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.stats`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.stats")

        return await es.indices.stats(index=self._index, **kwargs)

    async def upgrade(self, using=None, **kwargs):
        """
        Asynchronously upgrades the index to the latest format.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.upgrade`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.upgrade")

        return await es.indices.upgrade(index=self._index, **kwargs)

    async def validate_query(self, using=None, **kwargs):
        """
        Asynchronously validates a potentially expensive query without executing it.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.indices.validate_query`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "AsyncIndex.validate_query")

        return await es.indices.validate_query(index=self._index, **kwargs)


class AsyncIndexTemplate(IndexTemplate):
    async def save(self, using=None):
        es = get_connection(using or self._index._using)
        ensure_async_connection(es, "AsyncIndexTemplate.save")

        return await es.indices.put_template(
            name=self._template_name, body=self.to_dict()
        )
