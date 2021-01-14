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

try:
    import collections.abc as collections_abc  # only works on python 3.3+
except ImportError:
    import collections as collections_abc

from six import string_types

from ..aggs import AggBase
from ..query import Q
from ..response import Hit, Response
from ..utils import DslBase


class QueryProxy(object):
    """
    Simple proxy around DSL objects (queries) that can be called
    (to add query/post_filter) and also allows attribute access which is proxied to
    the wrapped query.
    """

    def __init__(self, search, attr_name):
        self._search = search
        self._proxied = None
        self._attr_name = attr_name

    def __nonzero__(self):
        return self._proxied is not None

    __bool__ = __nonzero__

    def __call__(self, *args, **kwargs):
        s = self._search._clone()

        # we cannot use self._proxied since we just cloned self._search and
        # need to access the new self on the clone
        proxied = getattr(s, self._attr_name)
        if proxied._proxied is None:
            proxied._proxied = Q(*args, **kwargs)
        else:
            proxied._proxied &= Q(*args, **kwargs)

        # always return search to be chainable
        return s

    def __getattr__(self, attr_name):
        return getattr(self._proxied, attr_name)

    def __setattr__(self, attr_name, value):
        if not attr_name.startswith("_"):
            self._proxied = Q(self._proxied.to_dict())
            setattr(self._proxied, attr_name, value)
        super(QueryProxy, self).__setattr__(attr_name, value)

    def __getstate__(self):
        return self._search, self._proxied, self._attr_name

    def __setstate__(self, state):
        self._search, self._proxied, self._attr_name = state


class ProxyDescriptor(object):
    """
    Simple descriptor to enable setting of queries and filters as:

        s = Search()
        s.query = Q(...)

    """

    def __init__(self, name):
        self._attr_name = "_%s_proxy" % name

    def __get__(self, instance, owner):
        return getattr(instance, self._attr_name)

    def __set__(self, instance, value):
        proxy = getattr(instance, self._attr_name)
        proxy._proxied = Q(value)


class AggsProxy(AggBase, DslBase):
    name = "aggs"

    def __init__(self, search):
        self._base = self
        self._search = search
        self._params = {"aggs": {}}

    def to_dict(self):
        return super(AggsProxy, self).to_dict().get("aggs", {})


class Request(object):
    def __init__(self, using="default", index=None, doc_type=None, extra=None):
        self._using = using

        self._index = None
        if isinstance(index, (tuple, list)):
            self._index = list(index)
        elif index:
            self._index = [index]

        self._doc_type = []
        self._doc_type_map = {}
        if isinstance(doc_type, (tuple, list)):
            self._doc_type.extend(doc_type)
        elif isinstance(doc_type, collections_abc.Mapping):
            self._doc_type.extend(doc_type.keys())
            self._doc_type_map.update(doc_type)
        elif doc_type:
            self._doc_type.append(doc_type)

        self._params = {}
        self._extra = extra or {}

    def __eq__(self, other):
        return (
            isinstance(other, Request)
            and other._params == self._params
            and other._index == self._index
            and other._doc_type == self._doc_type
            and other.to_dict() == self.to_dict()
        )

    def __copy__(self):
        return self._clone()

    def params(self, **kwargs):
        """
        Specify query params to be used when executing the search. All the
        keyword arguments will override the current values. See
        https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.Elasticsearch.search
        for all available parameters.

        Example::

            s = Search()
            s = s.params(routing='user-1', preference='local')
        """
        s = self._clone()
        s._params.update(kwargs)
        return s

    def index(self, *index):
        """
        Set the index for the search. If called empty it will remove all information.

        Example:

            s = Search()
            s = s.index('twitter-2015.01.01', 'twitter-2015.01.02')
            s = s.index(['twitter-2015.01.01', 'twitter-2015.01.02'])
        """
        # .index() resets
        s = self._clone()
        if not index:
            s._index = None
        else:
            indexes = []
            for i in index:
                if isinstance(i, string_types):
                    indexes.append(i)
                elif isinstance(i, list):
                    indexes += i
                elif isinstance(i, tuple):
                    indexes += list(i)

            s._index = (self._index or []) + indexes

        return s

    def _resolve_field(self, path):
        for dt in self._doc_type:
            if not hasattr(dt, "_index"):
                continue
            field = dt._index.resolve_field(path)
            if field is not None:
                return field

    def _resolve_nested(self, hit, parent_class=None):
        doc_class = Hit

        nested_path = []
        nesting = hit["_nested"]
        while nesting and "field" in nesting:
            nested_path.append(nesting["field"])
            nesting = nesting.get("_nested")
        nested_path = ".".join(nested_path)

        if hasattr(parent_class, "_index"):
            nested_field = parent_class._index.resolve_field(nested_path)
        else:
            nested_field = self._resolve_field(nested_path)

        if nested_field is not None:
            return nested_field._doc_class

        return doc_class

    def _get_result(self, hit, parent_class=None):
        doc_class = Hit
        dt = hit.get("_type")

        if "_nested" in hit:
            doc_class = self._resolve_nested(hit, parent_class)

        elif dt in self._doc_type_map:
            doc_class = self._doc_type_map[dt]

        else:
            for doc_type in self._doc_type:
                if hasattr(doc_type, "_matches") and doc_type._matches(hit):
                    doc_class = doc_type
                    break

        for t in hit.get("inner_hits", ()):
            hit["inner_hits"][t] = Response(
                self, hit["inner_hits"][t], doc_class=doc_class
            )

        callback = getattr(doc_class, "from_es", doc_class)
        return callback(hit)

    def doc_type(self, *doc_type, **kwargs):
        """
        Set the type to search through. You can supply a single value or
        multiple. Values can be strings or subclasses of ``Document``.

        You can also pass in any keyword arguments, mapping a doc_type to a
        callback that should be used instead of the Hit class.

        If no doc_type is supplied any information stored on the instance will
        be erased.

        Example:

            s = Search().doc_type('product', 'store', User, custom=my_callback)
        """
        # .doc_type() resets
        s = self._clone()
        if not doc_type and not kwargs:
            s._doc_type = []
            s._doc_type_map = {}
        else:
            s._doc_type.extend(doc_type)
            s._doc_type.extend(kwargs.keys())
            s._doc_type_map.update(kwargs)
        return s

    def using(self, client):
        """
        Associate the search request with an elasticsearch client. A fresh copy
        will be returned with current instance remaining unchanged.

        :arg client: an instance of ``elasticsearch.Elasticsearch`` to use or
            an alias to look up in ``elasticsearch_dsl.connections``

        """
        s = self._clone()
        s._using = client
        return s

    def extra(self, **kwargs):
        """
        Add extra keys to the request body. Mostly here for backwards
        compatibility.
        """
        s = self._clone()
        if "from_" in kwargs:
            kwargs["from"] = kwargs.pop("from_")
        s._extra.update(kwargs)
        return s

    def _clone(self):
        s = self.__class__(
            using=self._using, index=self._index, doc_type=self._doc_type
        )
        s._doc_type_map = self._doc_type_map.copy()
        s._extra = self._extra.copy()
        s._params = self._params.copy()
        return s
