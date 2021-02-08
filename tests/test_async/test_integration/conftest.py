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

from pytest import fixture, mark, skip

from elasticsearch_dsl.connections import add_connection

pytestmark = mark.asyncio


@fixture(scope="function", autouse=True)
async def async_client():
    try:
        from elasticsearch import AsyncElasticsearch
    except ImportError:
        return skip("asyncio support must be available")
    try:
        connection = AsyncElasticsearch("http://localhost:9200")
        await connection.info()
    except Exception:
        return skip("Couldn't connect to Elasticsearch")

    add_connection("async", connection)
    return connection


@fixture
async def write_client(async_client):
    yield async_client
    await async_client.indices.delete("test-*", ignore=404)
    await async_client.indices.delete_template("test-template", ignore=404)
