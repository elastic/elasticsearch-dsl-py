from datetime import date
from pytest import raises, fixture

from elasticsearch_dsl import response, Search, DocType, Date, Object
from elasticsearch_dsl.aggs import Terms
from elasticsearch_dsl.response.aggs import AggData, BucketData, Bucket

@fixture
def agg_response(aggs_search, aggs_data):
    return response.Response(aggs_search, aggs_data)

def test_response_stores_search(dummy_response):
    s = Search()
    r = response.Response(s, dummy_response)

    assert r._search is s

def test_attribute_error_in_hits_is_not_hidden(dummy_response):
    def f(hit):
        raise AttributeError()

    s = Search().doc_type(employee=f)
    r = response.Response(s, dummy_response)
    with raises(TypeError):
        r.hits

def test_interactive_helpers(dummy_response):
    res = response.Response(Search(), dummy_response)
    hits = res.hits
    h = hits[0]

    rhits = "[<Hit(test-index/company/elasticsearch): %s>, <Hit(test-index/employee/42): %s...}>, <Hit(test-index/employee/47): %s...}>, <Hit(test-index/employee/53): {}>]" % (
            repr(dummy_response['hits']['hits'][0]['_source']),
            repr(dummy_response['hits']['hits'][1]['_source'])[:60],
            repr(dummy_response['hits']['hits'][2]['_source'])[:60],
            )

    assert res
    assert '<Response: %s>' % rhits == repr(res)
    assert rhits == repr(hits)
    assert set(['meta', 'city', 'name']) == set(dir(h))
    assert "<Hit(test-index/company/elasticsearch): %r>" % dummy_response['hits']['hits'][0]['_source'] == repr(h)

def test_empty_response_is_false(dummy_response):
    dummy_response['hits']['hits'] = []
    res = response.Response(Search(), dummy_response)

    assert not res

def test_len_response(dummy_response):
    res = response.Response(Search(), dummy_response)
    assert len(res) == 4

def test_iterating_over_response_gives_you_hits(dummy_response):
    res = response.Response(Search(), dummy_response)
    hits = list(h for h in res)

    assert res.success()
    assert 123 == res.took
    assert 4 == len(hits)
    assert all(isinstance(h, response.Hit) for h in hits)
    h = hits[0]

    assert 'test-index' == h.meta.index
    assert 'company' == h.meta.doc_type
    assert 'elasticsearch' == h.meta.id
    assert 12 == h.meta.score

    assert hits[1].meta.parent == 'elasticsearch'

def test_hits_get_wrapped_to_contain_additional_attrs(dummy_response):
    res = response.Response(Search(), dummy_response)
    hits = res.hits

    assert 123 == hits.total
    assert 12.0 == hits.max_score

def test_hits_provide_dot_and_bracket_access_to_attrs(dummy_response):
    res = response.Response(Search(), dummy_response)
    h = res.hits[0]

    assert 'Elasticsearch' == h.name
    assert 'Elasticsearch' == h['name']

    assert 'Honza' == res.hits[2].name.first

    with raises(KeyError):
        h['not_there']

    with raises(AttributeError):
        h.not_there

def test_slicing_on_response_slices_on_hits(dummy_response):
    res = response.Response(Search(), dummy_response)

    assert res[0] is res.hits[0]
    assert res[::-1] == res.hits[::-1]

def test_aggregation_base(agg_response):
    assert agg_response.aggs is agg_response.aggregations
    assert isinstance(agg_response.aggs, response.AggResponse)

def test_aggregations_can_be_iterated_over(agg_response):
    aggs = [a for a in agg_response.aggs]

    assert len(aggs) == 2
    assert all(map(lambda a: isinstance(a, AggData), aggs))

def test_aggregations_can_be_retrieved_by_name(agg_response, aggs_search):
    a = agg_response.aggs['popular_files']

    assert isinstance(a, BucketData)
    assert isinstance(a.meta.agg, Terms)
    assert a.meta.agg is aggs_search.aggs.aggs['popular_files']

def test_bucket_response_can_be_iterated_over(agg_response):
    popular_files = agg_response.aggregations.popular_files

    buckets = [b for b in popular_files]
    assert all(isinstance(b, Bucket) for b in buckets)
    assert buckets == popular_files.buckets

def test_bucket_keys_get_deserialized(aggs_data, aggs_search):
    class Commit(DocType):
        info = Object(properties={'committed_date': Date()})
    aggs_search._doc_type_map = {'commit': Commit}
    agg_response = response.Response(aggs_search, aggs_data)

    per_month = agg_response.aggregations.per_month
    for b in per_month:
        assert isinstance(b.key, date)
