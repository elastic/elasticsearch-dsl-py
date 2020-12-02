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

import pickle

from pytest import raises

from elasticsearch_dsl import serializer, utils


def test_attrdict_pickle():
    ad = utils.AttrDict({})

    pickled_ad = pickle.dumps(ad)
    assert ad == pickle.loads(pickled_ad)


def test_attrlist_pickle():
    al = utils.AttrList([])

    pickled_al = pickle.dumps(al)
    assert al == pickle.loads(pickled_al)


def test_attrlist_slice():
    class MyAttrDict(utils.AttrDict):
        pass

    l = utils.AttrList([{}, {}], obj_wrapper=MyAttrDict)
    assert isinstance(l[:][0], MyAttrDict)


def test_merge():
    a = utils.AttrDict({"a": {"b": 42, "c": 47}})
    b = {"a": {"b": 123, "d": -12}, "e": [1, 2, 3]}

    utils.merge(a, b)

    assert a == {"a": {"b": 123, "c": 47, "d": -12}, "e": [1, 2, 3]}


def test_merge_conflict():
    for d in (
        {"a": 42},
        {"a": {"b": 47}},
    ):
        utils.merge({"a": {"b": 42}}, d)
        with raises(ValueError):
            utils.merge({"a": {"b": 42}}, d, True)


def test_attrdict_bool():
    d = utils.AttrDict({})

    assert not d
    d.title = "Title"
    assert d


def test_attrlist_items_get_wrapped_during_iteration():
    al = utils.AttrList([1, object(), [1], {}])

    l = list(iter(al))

    assert isinstance(l[2], utils.AttrList)
    assert isinstance(l[3], utils.AttrDict)


def test_serializer_deals_with_Attr_versions():
    d = utils.AttrDict({"key": utils.AttrList([1, 2, 3])})

    assert serializer.serializer.dumps(d) == serializer.serializer.dumps(
        {"key": [1, 2, 3]}
    )


def test_serializer_deals_with_objects_with_to_dict():
    class MyClass(object):
        def to_dict(self):
            return 42

    assert serializer.serializer.dumps(MyClass()) == "42"
