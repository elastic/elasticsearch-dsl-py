from pytest import raises, mark

from elasticsearch_dsl import result

@mark.xfail
def test_interactive_helpers(dummy_response):
    res = result.Response(dummy_response)
    hits = res.hits
    h = hits[0]

    rhits = "[<Result(test-index/company/elasticsearch): %s>, <Result(test-index/employee/42): %s...}>, <Result(test-index/employee/47): %s...}>, <Result(test-index/employee/53): {}>]" % (
            repr(dummy_response['hits']['hits'][0]['_source']),
            repr(dummy_response['hits']['hits'][1]['_source'])[:60],
            repr(dummy_response['hits']['hits'][2]['_source'])[:60],
            )

    assert res
    assert '<Response: %s>' % rhits == repr(res)
    assert rhits == repr(hits)
    assert set(['meta', 'city', 'name']) == set(dir(h))
    assert h._meta
    assert "<Result(test-index/company/elasticsearch): %r>" % dummy_response['hits']['hits'][0]['_source'] == repr(h)

def test_enpty_response_is_false(dummy_response):
    dummy_response['hits']['hits'] = []
    res = result.Response(dummy_response)

    assert not res

def test_iterating_over_response_gives_you_hits(dummy_response):
    res = result.Response(dummy_response)
    hits = list(h for h in res)

    assert res.success()
    assert 123 == res.took
    assert 4 == len(hits)
    assert all(isinstance(h, result.Result) for h in hits)
    h = hits[0]

    assert 'test-index' == h.meta.index
    assert 'company' == h.meta.doc_type
    assert 'elasticsearch' == h.meta.id
    assert 12 == h.meta.score

    assert hits[1].meta.parent == 'elasticsearch'

def test_hits_get_wrapped_to_contain_additional_attrs(dummy_response):
    res = result.Response(dummy_response)
    hits = res.hits

    assert 123 == hits.total
    assert 12.0 == hits.max_score

def test_hits_provide_dot_and_bracket_access_to_attrs(dummy_response):
    res = result.Response(dummy_response)
    h = res.hits[0]

    assert 'Elasticsearch' == h.name
    assert 'Elasticsearch' == h['name']
    assert 'Elasticsearch' == h.get('name')

    assert 'Honza' == res.hits[2].name.first

    with raises(KeyError):
        h['not_there']

    with raises(AttributeError):
        h.not_there

    assert None == h.get('not_there')

def test_slicing_on_response_slices_on_hits(dummy_response):
    res = result.Response(dummy_response)

    assert res[0] is res.hits[0]
    assert res[::-1] == res.hits[::-1]

