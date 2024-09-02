from typing import Any, Dict, List, Literal, Mapping, Union
from elasticsearch_dsl.document_base import InstrumentedField
from elasticsearch_dsl import function as f, interfaces as i, Query
from elasticsearch_dsl.utils import AttrDict, NotSet, NOT_SET

PipeSeparatedFlags = str


{% for k in classes %}
class {{ k.name }}({% if k.parent %}{{ k.parent }}{% else %}AttrDict[Any]{% endif %}):
    {% if k.properties %}
    """
    {% for p in k.properties %}
    {% for line in p.doc %}
    {{ line }}
    {% endfor %}
    {% endfor %}
    """
    {% for p in k.properties %}
    {{ p.name }}: {{ p.type }}
    {% endfor %}

    def __init__(
        self,
        *,
        {% for p in k.properties %}
        {{ p.name }}: {{ p.type }} = NOT_SET,
        {% endfor %}
        **kwargs: Any
    ):
        {% for p in k.properties %}
        if not isinstance({{ p.name }}, NotSet):
            {% if "InstrumentedField" in p.type %}
            kwargs["{{ p.name }}"] = str({{ p.name }})
            {% else %}
            kwargs["{{ p.name }}"] = {{ p.name }}
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
