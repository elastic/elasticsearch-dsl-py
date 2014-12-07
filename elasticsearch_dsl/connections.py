from six import string_types

from elasticsearch import Elasticsearch

class Connections(object):
    def __init__(self):
        self._kwargs = {}
        self._conns = {}

    def configure(self, **kwargs):
        for k in list(self._conns):
            # try and preserve existing client to keep the persistent connections alive
            if k in self._kwargs and kwargs.get(k, None) == self._kwargs[k]:
                continue
            del self._conns[k]
        self._kwargs = kwargs

    def add_connection(self, alias, conn):
        self._conns[alias] = conn

    def remove_connection(self, alias):
        errors = 0
        for d in (self._conns, self._kwargs):
            try:
                del d[alias]
            except KeyError:
                errors += 1

        if errors == 2:
            raise KeyError('There is no connection with alias %r.' % alias)

    def create_connection(self, alias='default', **kwargs):
        conn = self._conns[alias] = Elasticsearch(**kwargs)
        return conn

    def get_connection(self, alias='default'):
        # do not check isinstance(Elasticsearch) so that people can wrap their
        # clients
        if not isinstance(alias, string_types):
            return alias

        # connection already established
        try:
            return self._conns[alias]
        except KeyError:
            pass

        # if not, try to create it
        try:
            conn = self._conns[alias] = Elasticsearch(**self._kwargs[alias])
        except KeyError:
            # no connection and no kwargs to set one up
            raise KeyError('There is no connection with alias %r.' % alias)
        else:
            return conn

connections = Connections()
