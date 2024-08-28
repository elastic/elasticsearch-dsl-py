from typing import Any, List, Literal, Mapping, TypedDict, Union
from elasticsearch_dsl.search_base import InstrumentedField
from elasticsearch_dsl import analysis, function, interfaces as i, Query

PipeSeparatedFlags = str


{% for k in classes %}
class {{ k.name }}({% if k.parent %}{{ k.parent }}{% else %}TypedDict{% endif %}):
    {% if k.properties %}
    {% for p in k.properties %}
    {{ p.name }}: {{ p.type }}
    {% endfor %}
    {% else %}
    pass
    {% endif %}


{% endfor %}
