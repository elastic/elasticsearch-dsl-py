from typing import TYPE_CHECKING, Any, List, Literal, Mapping, TypedDict, Union
from elasticsearch_dsl.search_base import InstrumentedField
from elasticsearch_dsl.utils import AttrDict

if TYPE_CHECKING:
    from elasticsearch_dsl import analysis, function, wrappers

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
