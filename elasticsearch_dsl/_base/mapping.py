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

from six import itervalues

from ..field import construct_field
from ..utils import DslBase


class Properties(DslBase):
    name = "properties"
    _param_defs = {"properties": {"type": "field", "hash": True}}

    def __init__(self):
        super(Properties, self).__init__()

    def __repr__(self):
        return "Properties()"

    def __getitem__(self, name):
        return self.properties[name]

    def __contains__(self, name):
        return name in self.properties

    def to_dict(self):
        return super(Properties, self).to_dict()["properties"]

    def field(self, name, *args, **kwargs):
        self.properties[name] = construct_field(*args, **kwargs)
        return self

    def _collect_fields(self):
        """ Iterate over all Field objects within, including multi fields. """
        for f in itervalues(self.properties.to_dict()):
            yield f
            # multi fields
            if hasattr(f, "fields"):
                for inner_f in itervalues(f.fields.to_dict()):
                    yield inner_f
            # nested and inner objects
            if hasattr(f, "_collect_fields"):
                for inner_f in f._collect_fields():
                    yield inner_f

    def update(self, other_object):
        if not hasattr(other_object, "properties"):
            # not an inner/nested object, no merge possible
            return

        our, other = self.properties, other_object.properties
        for name in other:
            if name in our:
                if hasattr(our[name], "update"):
                    our[name].update(other[name])
                continue
            our[name] = other[name]
