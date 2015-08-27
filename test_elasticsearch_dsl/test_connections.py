from elasticsearch import Elasticsearch

from elasticsearch_dsl import connections, serializer

from pytest import raises

def test_default_connection_is_returned_by_default():
    c = connections.Connections()

    con, con2 = object(), object()
    c.add_connection('default', con)

    c.add_connection('not-default', con2)

    assert c.get_connection() is con

def test_get_connection_created_connection_if_needed():
    c = connections.Connections()
    c.configure(default={'hosts': ['es.com']}, local={'hosts': ['localhost']})

    default = c.get_connection()
    local = c.get_connection('local')

    assert isinstance(default, Elasticsearch)
    assert isinstance(local, Elasticsearch)

    assert [{'host': 'es.com'}] == default.transport.hosts
    assert [{'host': 'localhost'}] == local.transport.hosts

def test_configure_preserves_unchanged_connections():
    c = connections.Connections()

    c.configure(default={'hosts': ['es.com']}, local={'hosts': ['localhost']})
    default = c.get_connection()
    local = c.get_connection('local')

    c.configure(default={'hosts': ['not-es.com']}, local={'hosts': ['localhost']})
    new_default = c.get_connection()
    new_local = c.get_connection('local')

    assert new_local is local
    assert new_default is not default

def test_remove_connection_removes_both_conn_and_conf():
    c = connections.Connections()

    c.configure(default={'hosts': ['es.com']}, local={'hosts': ['localhost']})
    c.add_connection('local2', object())

    c.remove_connection('default')
    c.get_connection('local2')
    c.remove_connection('local2')

    with raises(Exception):
        c.get_connection('local2')
        c.get_connection('default')

def test_create_connection_constructs_client():
    c = connections.Connections()
    c.create_connection('testing', hosts=['es.com'])

    con = c.get_connection('testing')
    assert [{'host': 'es.com'}] == con.transport.hosts

def test_create_connection_adds_our_serializer():
    c = connections.Connections()
    c.create_connection('testing', hosts=['es.com'])

    assert c.get_connection('testing').transport.serializer is serializer.serializer
