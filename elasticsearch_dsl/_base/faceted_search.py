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

from six import iteritems

from ..response import Response
from ..utils import AttrDict


class FacetedResponse(Response):
    @property
    def query_string(self):
        return self._faceted_search._query

    @property
    def facets(self):
        if not hasattr(self, "_facets"):
            super(AttrDict, self).__setattr__("_facets", AttrDict({}))
            for name, facet in iteritems(self._faceted_search.facets):
                self._facets[name] = facet.get_values(
                    getattr(getattr(self.aggregations, "_filter_" + name), name),
                    self._faceted_search.filter_values.get(name, ()),
                )
        return self._facets
