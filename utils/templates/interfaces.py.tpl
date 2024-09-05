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

from typing import Any, Dict, List, Literal, Mapping, Union

from elastic_transport.client_utils import DEFAULT, DefaultType

from elasticsearch_dsl.document_base import InstrumentedField
from elasticsearch_dsl import function as f, interfaces as i, Query
from elasticsearch_dsl.utils import AttrDict

PipeSeparatedFlags = str


{% for k in classes %}
class {{ k.name }}({% if k.parent %}{{ k.parent }}{% else %}AttrDict[Any]{% endif %}):
    {% if k.args %}
    """
    {% for arg in k.args %}
    {% for line in arg.doc %}
    {{ line }}
    {% endfor %}
    {% endfor %}
    """
    {% for arg in k.args %}
    {{ arg.name }}: {{ arg.type }}
    {% endfor %}

    def __init__(
        self,
        *,
        {% for arg in k.args %}
        {{ arg.name }}: {{ arg.type }} = DEFAULT,
        {% endfor %}
        **kwargs: Any
    ):
        {% for arg in k.args %}
        if {{ arg.name }} != DEFAULT:
            {% if "InstrumentedField" in arg.type %}
            kwargs["{{ arg.name }}"] = str({{ arg.name }})
            {% else %}
            kwargs["{{ arg.name }}"] = {{ arg.name }}
            {% endif %}
        {% endfor %}
        {% if k.parent %}
        super().__init__(**kwargs)
        {% else %}
        super().__init__(kwargs)
        {% endif %}
    {% else %}
    pass
    {% endif %}


{% endfor %}
