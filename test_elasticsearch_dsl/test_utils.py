from elasticsearch_dsl import utils


def test_attrdict_bool():
    d = utils.AttrDict({})

    assert not d
    d.title = 'Title'
    assert d


def test_attrlist_items_get_wrapped_during_iteration():
    al = utils.AttrList([1, object(), [1], {}])

    l = list(iter(al))

    assert isinstance(l[2], utils.AttrList)
    assert isinstance(l[3], utils.AttrDict)


def test_make_dsl_class():
    XY = utils._make_dsl_class(object, 'X', suffix='Y')

    assert XY.__name__ == 'XY'
    assert XY.__bases__ == (object, )
