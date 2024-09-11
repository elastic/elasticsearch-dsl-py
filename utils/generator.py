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

import json
import re
import textwrap
from urllib.error import HTTPError
from urllib.request import urlopen

from jinja2 import Environment, PackageLoader, select_autoescape

from elasticsearch_dsl import VERSION

jinja_env = Environment(
    loader=PackageLoader("utils"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)
query_py = jinja_env.get_template("query.py.tpl")
types_py = jinja_env.get_template("types.py.tpl")

# map with name replacements for Elasticsearch attributes
PROP_REPLACEMENTS = {"from": "from_"}

# map with Elasticsearch type replacements
# keys and values are in given in "{namespace}:{name}" format
TYPE_REPLACEMENTS = {
    "_types.query_dsl:DistanceFeatureQuery": "_types.query_dsl:DistanceFeatureQueryBase",
}


def wrapped_doc(text, width=70, initial_indent="", subsequent_indent=""):
    """Formats a docstring as a list of lines of up to the request width."""
    return textwrap.wrap(
        text.replace("\n", " "),
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
    )


def add_dict_type(type_):
    """Add Dict[str, Any] to a Python type hint."""
    if type_.startswith("Union["):
        type_ = f"{type_[:-1]}, Dict[str, Any]]"
    else:
        type_ = f"Union[{type_}, Dict[str, Any]]"
    return type_


def add_not_set(type_):
    """Add DefaultType to a Python type hint."""
    if type_.startswith("Union["):
        type_ = f'{type_[:-1]}, "DefaultType"]'
    else:
        type_ = f'Union[{type_}, "DefaultType"]'
    return type_


class ElasticsearchSchema:
    """Operations related to the Elasticsearch schema."""

    def __init__(self):
        response = None
        for branch in [f"{VERSION[0]}.{VERSION[1]}", "main"]:
            url = f"https://raw.githubusercontent.com/elastic/elasticsearch-specification/{branch}/output/schema/schema.json"
            try:
                response = urlopen(url)
                print(f"Initializing code generation with '{branch}' specification.")
                break
            except HTTPError:
                continue
        if not response:
            raise RuntimeError("Could not download Elasticsearch schema")
        self.schema = json.loads(response.read())

        # Interfaces collects interfaces that are seen while traversing the schema.
        # Any interfaces collected here are then rendered as Python in the
        # types.py module.
        self.interfaces = []

    def find_type(self, name, namespace=None):
        for t in self.schema["types"]:
            if t["name"]["name"] == name and (
                namespace is None or t["name"]["namespace"] == namespace
            ):
                return t

    def get_python_type(self, schema_type):
        """Obtain Python typing details for a given schema type

        This method returns a tuple. The first element is a string with the
        Python type hint. The second element is a dictionary with Python DSL
        specific typing details to be stored in the DslBase._param_defs
        attribute (or None if the type does not need to be in _param_defs).
        """
        if schema_type["kind"] == "instance_of":
            type_name = schema_type["type"]
            if type_name["namespace"] in ["_types", "internal", "_builtins"]:
                if type_name["name"] in ["integer", "uint", "long", "ulong"]:
                    return "int", None
                elif type_name["name"] in ["number", "float", "double"]:
                    return "float", None
                elif type_name["name"] == "string":
                    return "str", None
                elif type_name["name"] == "boolean":
                    return "bool", None
                elif type_name["name"] == "binary":
                    return "bytes", None
                elif type_name["name"] == "null":
                    return "None", None
                elif type_name["name"] == "Field":
                    return 'Union[str, "InstrumentedField"]', None
                else:
                    # not an instance of a native type, so we get the type and try again
                    return self.get_python_type(
                        self.find_type(type_name["name"], type_name["namespace"])
                    )
            elif (
                type_name["namespace"] == "_types.query_dsl"
                and type_name["name"] == "QueryContainer"
            ):
                # QueryContainer maps to the DSL's Query class
                return "Query", {"type": "query"}
            else:
                # for any other instances we get the type and recurse
                type_ = self.find_type(type_name["name"], type_name["namespace"])
                if type_:
                    return self.get_python_type(type_)

        elif schema_type["kind"] == "type_alias":
            # for an alias, we use the aliased type
            return self.get_python_type(schema_type["type"])

        elif schema_type["kind"] == "array_of":
            # for arrays we use Sequence[element_type]
            type_, param = self.get_python_type(schema_type["value"])
            return f"Sequence[{type_}]", {**param, "multi": True} if param else None

        elif schema_type["kind"] == "dictionary_of":
            # for dicts we use Mapping[key_type, value_type]
            key_type, key_param = self.get_python_type(schema_type["key"])
            value_type, value_param = self.get_python_type(schema_type["value"])
            return f"Mapping[{key_type}, {value_type}]", None

        elif schema_type["kind"] == "union_of":
            if (
                len(schema_type["items"]) == 2
                and schema_type["items"][0]["kind"] == "instance_of"
                and schema_type["items"][1]["kind"] == "array_of"
                and schema_type["items"][0] == schema_type["items"][1]["value"]
            ):
                # special kind of unions in the form Union[type, Sequence[type]]
                type_, param = self.get_python_type(schema_type["items"][0])
                return (
                    f"Union[{type_}, Sequence[{type_}]]",
                    ({"type": param["type"], "multi": True} if param else None),
                )
            elif (
                len(schema_type["items"]) == 2
                and schema_type["items"][0]["kind"] == "instance_of"
                and schema_type["items"][1]["kind"] == "instance_of"
                and schema_type["items"][0]["type"]
                == {"name": "T", "namespace": "_spec_utils.PipeSeparatedFlags"}
                and schema_type["items"][1]["type"]
                == {"name": "string", "namespace": "_builtins"}
            ):
                # for now we treat PipeSeparatedFlags as a special case
                if "PipeSeparatedFlags" not in self.interfaces:
                    self.interfaces.append("PipeSeparatedFlags")
                return '"types.PipeSeparatedFlags"', None
            else:
                # generic union type
                types = list(
                    dict.fromkeys(  # eliminate duplicates
                        [self.get_python_type(t) for t in schema_type["items"]]
                    )
                )
                return "Union[" + ", ".join([type_ for type_, _ in types]) + "]", None

        elif schema_type["kind"] == "enum":
            # enums are mapped to Literal[member, ...]
            return (
                "Literal["
                + ", ".join(
                    [f"\"{member['name']}\"" for member in schema_type["members"]]
                )
                + "]",
                None,
            )

        elif schema_type["kind"] == "interface":
            if schema_type["name"]["namespace"] == "_types.query_dsl":
                # handle specific DSL classes explicitly to map to existing
                # Python DSL classes
                if schema_type["name"]["name"].endswith("RangeQuery"):
                    return '"wrappers.Range[Any]"', None
                elif schema_type["name"]["name"].endswith("ScoreFunction"):
                    # When dropping Python 3.8, use `removesuffix("Function")` instead
                    name = schema_type["name"]["name"][:-8]
                    return f'"function.{name}"', None
                elif schema_type["name"]["name"].endswith("DecayFunction"):
                    return '"function.DecayFunction"', None
                elif schema_type["name"]["name"].endswith("Function"):
                    return f"\"function.{schema_type['name']['name']}\"", None
            elif schema_type["name"]["namespace"] == "_types.analysis" and schema_type[
                "name"
            ]["name"].endswith("Analyzer"):
                # not expanding analyzers at this time, maybe in the future
                return "str, Dict[str, Any]", None

            # to handle other interfaces we generate a type of the same name
            # and add the interface to the interfaces.py module
            if schema_type["name"]["name"] not in self.interfaces:
                self.interfaces.append(schema_type["name"]["name"])
            return f"\"types.{schema_type['name']['name']}\"", None
        elif schema_type["kind"] == "user_defined_value":
            # user_defined_value maps to Python's Any type
            return "Any", None

        raise RuntimeError(f"Cannot find Python type for {schema_type}")

    def add_attribute(self, k, arg, for_types_py=False):
        """Add an attribute to the internal representation of a class.

        This method adds the argument `arg` to the data structure for a class
        stored in `k`. In particular, the argument is added to the `k["args"]`
        list, making sure required arguments are first in the list. If the
        argument is of a type that needs Python DSL specific typing details to
        be stored in the DslBase._param_defs attribute, then this is added to
        `k["params"]`.

        When `for_types_py` is `True`, type hints are formatted in the most
        convenient way for the types.py file. When possible, double quotes are
        removed from types, and for types that are in the same file the quotes
        are kept to prevent forward references, but the "types." namespace is
        removed. When `for_types_py` is `False`, all non-native types use
        quotes and are namespaced.
        """
        try:
            type_, param = schema.get_python_type(arg["type"])
        except RuntimeError:
            type_ = "Any"
            param = None
        if type_ != "Any":
            if "types." in type_:
                type_ = add_dict_type(type_)  # interfaces can be given as dicts
            type_ = add_not_set(type_)
        if for_types_py:
            type_ = type_.replace('"DefaultType"', "DefaultType")
            type_ = type_.replace('"InstrumentedField"', "InstrumentedField")
            type_ = re.sub(r'"(function\.[a-zA-Z0-9_]+)"', r"\1", type_)
            type_ = re.sub(r'"types\.([a-zA-Z0-9_]+)"', r'"\1"', type_)
            type_ = re.sub(r'"(wrappers\.[a-zA-Z0-9_]+)"', r"\1", type_)
        required = "(required) " if arg["required"] else ""
        server_default = (
            f" Defaults to `{arg['serverDefault']}` if omitted."
            if arg.get("serverDefault")
            else ""
        )
        doc = wrapped_doc(
            f":arg {arg['name']}: {required}{arg.get('description', '')}{server_default}",
            subsequent_indent="    ",
        )
        arg = {
            "name": PROP_REPLACEMENTS.get(arg["name"], arg["name"]),
            "type": type_,
            "doc": doc,
            "required": arg["required"],
        }
        if param is not None:
            param = {"name": arg["name"], "param": param}
        if arg["required"]:
            # insert in the right place so that all required arguments
            # appear at the top of the argument list
            i = 0
            for i in range(len(k["args"]) + 1):
                if i == len(k["args"]):
                    break
                if k["args"][i].get("positional"):
                    continue
                if k["args"][i]["required"] is False:
                    break
            k["args"].insert(i, arg)
        else:
            k["args"].append(arg)
        if param and "params" in k:
            k["params"].append(param)

    def property_to_python_class(self, p):
        """Return a dictionary with template data necessary to render a schema
        property as a Python class.

        Used for "container" sub-classes such as `QueryContainer`, where each
        sub-class is represented by a Python DSL class.

        The format is as follows:

        ```python
        {
            "property_name": "the name of the property",
            "name": "the class name to use for the property",
            "docstring": "the formatted docstring as a list of strings",
            "args": [  # a Python description of each class attribute
                "name": "the name of the attribute",
                "type": "the Python type hint for the attribute",
                "doc": ["formatted lines of documentation to add to class docstring"],
                "required": bool,
                "positional": bool,
            ],
            "params": [
                "name": "the attribute name",
                "param": "the param dictionary to include in `_param_defs` for the class",
            ],  # a DSL-specific description of interesting attributes
            "is_single_field": bool  # True for single-key dicts with field key
            "is_multi_field": bool  # True for multi-key dicts with field keys
        }
        ```
        """
        k = {
            "property_name": p["name"],
            "name": "".join([w.title() for w in p["name"].split("_")]),
        }
        k["docstring"] = wrapped_doc(p.get("description") or "")
        kind = p["type"]["kind"]
        if kind == "instance_of":
            namespace = p["type"]["type"]["namespace"]
            name = p["type"]["type"]["name"]
            if f"{namespace}:{name}" in TYPE_REPLACEMENTS:
                namespace, name = TYPE_REPLACEMENTS[f"{namespace}:{name}"].split(":")
            type_ = schema.find_type(name, namespace)
            if type_["kind"] == "interface":
                k["args"] = []
                k["params"] = []
                if "behaviors" in type_:
                    for behavior in type_["behaviors"]:
                        if (
                            behavior["type"]["name"] != "AdditionalProperty"
                            or behavior["type"]["namespace"] != "_spec_utils"
                        ):
                            # we do not support this behavior, so we ignore it
                            continue
                        key_type, _ = schema.get_python_type(behavior["generics"][0])
                        if "InstrumentedField" in key_type:
                            value_type, _ = schema.get_python_type(
                                behavior["generics"][1]
                            )
                            k["args"].append(
                                {
                                    "name": "_field",
                                    "type": add_not_set(key_type),
                                    "doc": [
                                        ":arg _field: The field to use in this query."
                                    ],
                                    "required": False,
                                    "positional": True,
                                }
                            )
                            k["args"].append(
                                {
                                    "name": "_value",
                                    "type": add_not_set(add_dict_type(value_type)),
                                    "doc": [
                                        ":arg _value: The query value for the field."
                                    ],
                                    "required": False,
                                    "positional": True,
                                }
                            )
                            k["is_single_field"] = True
                        else:
                            raise RuntimeError(
                                f"Non-field AdditionalProperty are not supported for interface {namespace}:{name}."
                            )
                while True:
                    for arg in type_["properties"]:
                        self.add_attribute(k, arg)
                    if "inherits" in type_ and "type" in type_["inherits"]:
                        type_ = schema.find_type(
                            type_["inherits"]["type"]["name"],
                            type_["inherits"]["type"]["namespace"],
                        )
                    else:
                        break
            else:
                raise RuntimeError(
                    f"Cannot generate code for instances of kind '{type_['kind']}'"
                )

        elif kind == "dictionary_of":
            key_type, _ = schema.get_python_type(p["type"]["key"])
            if "InstrumentedField" in key_type:
                value_type, _ = schema.get_python_type(p["type"]["value"])
                if p["type"]["singleKey"]:
                    # special handling for single-key dicts with field key
                    k["args"] = [
                        {
                            "name": "_field",
                            "type": add_not_set(key_type),
                            "doc": [":arg _field: The field to use in this query."],
                            "required": False,
                            "positional": True,
                        },
                        {
                            "name": "_value",
                            "type": add_not_set(add_dict_type(value_type)),
                            "doc": [":arg _value: The query value for the field."],
                            "required": False,
                            "positional": True,
                        },
                    ]
                    k["is_single_field"] = True
                else:
                    # special handling for multi-key dicts with field keys
                    k["args"] = [
                        {
                            "name": "_fields",
                            "type": f"Optional[Mapping[{key_type}, {value_type}]]",
                            "doc": [
                                ":arg _fields: A dictionary of fields with their values."
                            ],
                            "required": False,
                            "positional": True,
                        },
                    ]
                    k["is_multi_field"] = True
            else:
                raise RuntimeError(f"Cannot generate code for type {p['type']}")

        else:
            raise RuntimeError(f"Cannot generate code for type {p['type']}")
        return k

    def interface_to_python_class(self, interface, interfaces):
        """Return a dictionary with template data necessary to render an
        interface a Python class.

        This is used to render interfaces that are referenced by container
        classes. The current list of rendered interfaces is passed as a second
        argument to allow this method to add more interfaces to it as they are
        discovered.

        The returned format is as follows:

        ```python
        {
            "name": "the class name to use for the interface class",
            "parent": "the parent class name",
            "args": [ # a Python description of each class attribute
                "name": "the name of the attribute",
                "type": "the Python type hint for the attribute",
                "doc": ["formatted lines of documentation to add to class docstring"],
                "required": bool,
                "positional": bool,
            ],
        }
        ```
        """
        type_ = schema.find_type(interface)
        if type_["kind"] != "interface":
            raise RuntimeError(f"Type {interface} is not an interface")
        k = {"name": interface, "args": []}
        while True:
            for arg in type_["properties"]:
                schema.add_attribute(k, arg, for_types_py=True)

            if "inherits" not in type_ or "type" not in type_["inherits"]:
                break

            if "parent" not in k:
                k["parent"] = type_["inherits"]["type"]["name"]
            if type_["inherits"]["type"]["name"] not in interfaces:
                interfaces.append(type_["inherits"]["type"]["name"])
            type_ = schema.find_type(
                type_["inherits"]["type"]["name"],
                type_["inherits"]["type"]["namespace"],
            )
        return k


def generate_query_py(schema, filename):
    """Generate query.py with all the properties of `QueryContainer` as Python
    classes.
    """
    classes = []
    query_container = schema.find_type("QueryContainer", "_types.query_dsl")
    for p in query_container["properties"]:
        classes.append(schema.property_to_python_class(p))

    with open(filename, "wt") as f:
        f.write(query_py.render(classes=classes, parent="Query"))
    print(f"Generated {filename}.")


def generate_types_py(schema, filename):
    """Generate types.py"""
    classes = {}
    schema.interfaces = sorted(schema.interfaces)
    for interface in schema.interfaces:
        if interface == "PipeSeparatedFlags":
            continue  # handled as a special case
        k = schema.interface_to_python_class(interface, schema.interfaces)
        classes[k["name"]] = k

    classes_list = []
    for n in classes:
        k = classes[n]
        if k in classes_list:
            continue
        classes_list.append(k)
        parent = k.get("parent")
        parent_index = len(classes_list) - 1
        while parent:
            try:
                classes_list.index(classes[parent])
                break
            except ValueError:
                pass
            classes_list.insert(parent_index, classes[parent])
            parent = classes[parent].get("parent")

    with open(filename, "wt") as f:
        f.write(types_py.render(classes=classes_list))
    print(f"Generated {filename}.")


if __name__ == "__main__":
    schema = ElasticsearchSchema()
    generate_query_py(schema, "elasticsearch_dsl/query.py")
    generate_types_py(schema, "elasticsearch_dsl/types.py")
