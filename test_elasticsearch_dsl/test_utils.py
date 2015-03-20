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

def test_parent_dir():
    class MyAttrDict(utils.AttrDict):
        pass

    ad = MyAttrDict({'title': 'Title'})
    ad.title = 'Another title'
