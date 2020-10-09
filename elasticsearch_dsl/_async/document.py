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

from elasticsearch_dsl._async.utils import ensure_async_connection
from elasticsearch_dsl.document import Document


class AsyncDocument(Document):
    @classmethod
    async def get_async(cls, id, using=None, index=None, **kwargs):
        """
        Asynchronously retrieves a single document from elasticsearch using its ``id``.

        :arg id: ``id`` of the document to be retrieved
        :arg index: elasticsearch index to use, if the ``Document`` is
            associated with an index this can be omitted.
        :arg using: connection alias to use, defaults to ``'default'``

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.get`` unchanged.
        """
        es = cls._get_connection(using)
        ensure_async_connection(es, "Document.get_async")

        doc = await es.get(index=cls._default_index(index), id=id, **kwargs)
        if not doc.get("found", False):
            return None
        return cls.from_es(doc)

    @classmethod
    async def init_async(cls, index=None, using=None):
        """
        Asynchronously creates the index and populates the mappings in Elasticsearch.
        """
        i = cls._index
        if index:
            i = i.clone(name=index)
        await i.save(using=using)

    @classmethod
    async def mget_async(
        cls, docs, using=None, index=None, raise_on_error=True, missing="none", **kwargs
    ):
        r"""
        Asynchronously retrieves multiple documents by their ``id``\s. Returns a list
        of instances in the same order as requested.

        :arg docs: list of ``id``\s of the documents to be retrieved or a list
            of document specifications as per
            https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-multi-get.html
        :arg index: elasticsearch index to use, if the ``Document`` is
            associated with an index this can be omitted.
        :arg using: connection alias to use, defaults to ``'default'``
        :arg missing: what to do when one of the documents requested is not
            found. Valid options are ``'none'`` (use ``None``), ``'raise'`` (raise
            ``NotFoundError``) or ``'skip'`` (ignore the missing document).

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.mget`` unchanged.
        """
        if missing not in ("raise", "skip", "none"):
            raise ValueError("'missing' must be 'raise', 'skip', or 'none'.")

        es = cls._get_connection(using)
        ensure_async_connection(es, "Document.mget_async")

        results = await es.mget(
            cls._build_mget_body(docs),
            index=cls._default_index(index),
            **kwargs,
        )

        return cls._parse_mget_results(
            results,
            missing=missing,
            raise_on_error=raise_on_error,
        )

    async def delete_async(self, using=None, index=None, **kwargs):
        """
        Asynchronously deletes the instance in Elasticsearch.

        :arg index: elasticsearch index to use, if the ``Document`` is
            associated with an index this can be omitted.
        :arg using: connection alias to use, defaults to ``'default'``

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.delete`` unchanged.
        """
        es = self._get_connection(using)
        ensure_async_connection(es, "Document.delete_async")
        doc_meta = self._build_delete_doc_meta(**kwargs)
        await es.delete(index=self._get_index(index), **doc_meta)

    async def save_async(
        self, using=None, index=None, validate=True, skip_empty=True, **kwargs
    ):
        """
        Asyncrhonously saves the document into Elasticsearch. If the document doesn't
        exist it is created, otherwise it is overwritten. Returns ``True`` if this
        operation resulted in new document being created.

        :arg index: elasticsearch index to use, if the ``Document`` is
            associated with an index this can be omitted.
        :arg using: connection alias to use, defaults to ``'default'``
        :arg validate: set to ``False`` to skip validating the document
        :arg skip_empty: if set to ``False`` will cause empty values (``None``,
            ``[]``, ``{}``) to be left on the document. Those values will be
            stripped out otherwise as they make no difference in elasticsearch.

        Any additional keyword arguments will be passed to
        ``AsyncElasticsearch.index`` unchanged.

        :return operation result created/updated
        """
        if validate:
            self.full_clean()

        es = self._get_connection(using)
        ensure_async_connection(es, "Document.save_async")

        doc_meta = self._build_save_doc_meta(**kwargs)
        meta = await es.index(
            index=self._get_index(index),
            body=self.to_dict(skip_empty=skip_empty),
            **doc_meta,
        )
        self._update_doc_meta(meta)

        return meta["result"]

    async def update_async(
        self,
        using=None,
        index=None,
        detect_noop=True,
        doc_as_upsert=False,
        refresh=False,
        retry_on_conflict=None,
        script=None,
        script_id=None,
        scripted_upsert=False,
        upsert=None,
        **fields
    ):
        """
        Asynchronously performs a partial update of the document using the provided
        fields.

            doc = MyDocument(title='Document Title!')
            doc.save()
            doc.update(title='New Document Title!')

        :arg index: elasticsearch index to use, if the ``Document`` is
            associated with an index this can be omitted.
        :arg using: connection alias to use, defaults to ``'default'``
        :arg detect_noop: Set to ``False`` to disable noop detection.
        :arg refresh: Control when the changes made by this request are visible
            to search. Set to ``True`` for immediate effect.
        :arg retry_on_conflict: In between the get and indexing phases of the
            update, it is possible that another process might have already
            updated the same document. By default, the update will fail with a
            version conflict exception. The retry_on_conflict parameter
            controls how many times to retry the update before finally throwing
            an exception.
        :arg doc_as_upsert:  Instead of sending a partial doc plus an upsert
            doc, setting doc_as_upsert to true will use the contents of doc as
            the upsert value

        :return operation result noop/updated
        """
        body, doc_meta = self._build_update_body_and_meta(
            detect_noop=detect_noop,
            doc_as_upsert=doc_as_upsert,
            retry_on_conflict=retry_on_conflict,
            script=script,
            script_id=script_id,
            scripted_upsert=scripted_upsert,
            upsert=upsert,
            **fields,
        )

        es = self._get_connection(using)
        ensure_async_connection(es, "Document.update_async")

        meta = await es.update(
            index=self._get_index(index), body=body, refresh=refresh, **doc_meta
        )
        self._update_doc_meta(meta)

        return meta["result"]
