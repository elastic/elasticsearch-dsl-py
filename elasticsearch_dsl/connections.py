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

from elasticsearch import Elasticsearch
from six import string_types

from .serializer import serializer

try:
    from inspect import iscoroutinefunction
except ImportError:

    def iscoroutinefunction(_):
        return False


try:
    from elasticsearch import AsyncElasticsearch
except ImportError:
    AsyncElasticsearch = False


class Connections(object):
    """
    Class responsible for holding connections to different clusters. Used as a
    singleton in this module.
    """

    def __init__(self):
        self._kwargs = {}
        self._conns = {}

    def configure(self, **kwargs):
        """
        Configure multiple connections at once, useful for passing in config
        dictionaries obtained from other sources, like Django's settings or a
        configuration management tool.

        Example::

            connections.configure(
                default={'hosts': 'localhost'},
                dev={'hosts': ['esdev1.example.com:9200'], 'sniff_on_start': True},
            )

        Connections will only be constructed lazily when requested through
        ``get_connection``.
        """
        for k in list(self._conns):
            # try and preserve existing client to keep the persistent connections alive
            if k in self._kwargs and kwargs.get(k, None) == self._kwargs[k]:
                continue
            del self._conns[k]
        self._kwargs = kwargs

    def add_connection(self, alias, conn):
        """
        Add a connection object, it will be passed through as-is.
        """
        self._conns[alias] = conn

    def remove_connection(self, alias):
        """
        Remove connection from the registry. Raises ``KeyError`` if connection
        wasn't found.
        """
        errors = 0
        for d in (self._conns, self._kwargs):
            try:
                del d[alias]
            except KeyError:
                errors += 1

        if errors == 2:
            raise KeyError("There is no connection with alias %r." % alias)

    def create_connection(self, alias="default", is_async=False, **kwargs):
        """
        Construct an instance of ``elasticsearch.Elasticsearch`` and register
        it under given alias.
        """
        kwargs.setdefault("serializer", serializer)
        if is_async:
            try:
                from elasticsearch import AsyncElasticsearch
            except ImportError:
                # Raise a better error message
                raise ValueError(
                    "Could not import 'AsyncElasticsearch', "
                    "is 'elasticsearch[async]' installed?"
                )

            es_cls = AsyncElasticsearch
        else:
            es_cls = Elasticsearch
        conn = self._conns[alias] = es_cls(**kwargs)
        return conn

    def get_connection(self, alias="default", is_async=False):
        """
        Retrieve a connection, construct it if necessary (only configuration
        was passed to us). If a non-string alias has been passed through we
        assume it's already a client instance and will just return it as-is.

        Raises ``KeyError`` if no client (or its definition) is registered
        under the alias.
        """
        # do not check isinstance(Elasticsearch) so that people can wrap their
        # clients
        if not isinstance(alias, string_types):
            return alias

        # connection already established
        conn = None
        try:
            conn = self._conns[alias]
        except KeyError:
            # if not, try to create it
            try:
                conn = self.create_connection(
                    alias, is_async=is_async, **self._kwargs[alias]
                )
            except KeyError:
                # no connection and no kwargs to set one up
                raise KeyError("There is no connection with alias %r." % alias)

        # Verify if the client we got/created is async or sync like we want.
        if _is_async_client(conn) != is_async:
            raise ValueError(
                "Connection with alias %r %s"
                % (
                    alias,
                    # Change the error message depending on what
                    # connection type was requested.
                    "isn't async as requested"
                    if is_async
                    else "isn't sync as requested",
                )
            )

        return conn


def _is_async_client(client):
    """Detects an AsyncElasticsearch instance"""
    return (
        AsyncElasticsearch and isinstance(client, AsyncElasticsearch)
    ) or iscoroutinefunction(getattr(client, "search", None))


connections = Connections()
configure = connections.configure
add_connection = connections.add_connection
remove_connection = connections.remove_connection
create_connection = connections.create_connection
get_connection = connections.get_connection
