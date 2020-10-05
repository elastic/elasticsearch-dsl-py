from elasticsearch import AsyncElasticsearch


def ensure_async_connection(es, fn_label):
    if not isinstance(es, AsyncElasticsearch):
        raise TypeError(
            f"{fn_label} can only be used with the elasticsearch.AsyncElasticsearch "
            "client"
        )
