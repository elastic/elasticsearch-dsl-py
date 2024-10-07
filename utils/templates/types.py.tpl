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

from typing import Any, Dict, Literal, Mapping, Sequence, Union

from elastic_transport.client_utils import DEFAULT, DefaultType

from elasticsearch_dsl.document_base import InstrumentedField
from elasticsearch_dsl import function, Query
from elasticsearch_dsl.utils import AttrDict

PipeSeparatedFlags = str


{% for k in classes %}
class {{ k.name }}({{ k.parent if k.parent else "AttrDict[Any]" }}):
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
        {% for arg in k.args %}
        {% if arg.positional %}{{ arg.name }}: {{ arg.type }} = DEFAULT,{% endif %}
        {% endfor %}
        {% if k.args and not k.args[-1].positional %}
        *,
        {% endif %}
        {% for arg in k.args %}
        {% if not arg.positional %}{{ arg.name }}: {{ arg.type }} = DEFAULT,{% endif %}
        {% endfor %}
        **kwargs: Any
    ):
        {% if k.is_single_field %}
        if _field is not DEFAULT:
            kwargs[str(_field)] = _value
        {% elif k.is_multi_field %}
        if _fields is not DEFAULT:
            for field, value in _fields.items():
                kwargs[str(field)] = value
        {% endif %}
        {% for arg in k.args %}
            {% if not arg.positional %}
        if {{ arg.name }} is not DEFAULT:
                {% if "InstrumentedField" in arg.type %}
            kwargs["{{ arg.name }}"] = str({{ arg.name }})
                {% else %}
            kwargs["{{ arg.name }}"] = {{ arg.name }}
                {% endif %}
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
