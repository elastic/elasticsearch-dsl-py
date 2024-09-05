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
interfaces_py = jinja_env.get_template("interfaces.py.tpl")

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
        (text or "No documentation available.").replace("\n", " "),
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
    """Add NotSet to a Python type hint."""
    if type_.startswith("Union["):
        type_ = f'{type_[:-1]}, "NotSet"]'
    else:
        type_ = f'Union[{type_}, "NotSet"]'
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
        # interfaces.py module.
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
            # for arrays we use List[element_type]
            type_, param = self.get_python_type(schema_type["value"])
            return f"List[{type_}]", {**param, "multi": True} if param else None

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
                # special kind of unions in the form Union[type, List[type]]
                type_, param = self.get_python_type(schema_type["items"][0])
                return (
                    f"Union[{type_}, List[{type_}]]",
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
                return '"i.PipeSeparatedFlags"', None
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
                    name = schema_type["name"]["name"][:-8]
                    if name == "FieldValueFactorScore":
                        name = "FieldValueFactor"  # Python DSL uses different name
                    return f'"f.{name}"', None
                elif schema_type["name"]["name"].endswith("DecayFunction"):
                    return '"f.DecayFunction"', None
                elif schema_type["name"]["name"].endswith("Function"):
                    return f"\"f.{schema_type['name']['name']}\"", None
            elif schema_type["name"]["namespace"] == "_types.analysis" and schema_type[
                "name"
            ]["name"].endswith("Analyzer"):
                # not expanding analyzers at this time, maybe in the future
                return "str, Dict[str, Any]", None

            # to handle other interfaces we generate a type of the same name
            # and add the interface to the interfaces.py module
            if schema_type["name"]["name"] not in self.interfaces:
                self.interfaces.append(schema_type["name"]["name"])
            return f"\"i.{schema_type['name']['name']}\"", None
        elif schema_type["kind"] == "user_defined_value":
            # user_defined_value maps to Python's Any type
            return "Any", None

        raise RuntimeError(f"Cannot find Python type for {schema_type}")

    def get_attribute_data(self, arg):
        """Return the template definitions for a class attribute.

        This method returns a tuple. The first element is a dict with the
        information to render the attribute. The second element is a dictionary
        with Python DSL specific typing details to be stored in the
        DslBase._param_defs attribute (or None if the type does not need to be
        in _param_defs).
        """
        try:
            type_, param = schema.get_python_type(arg["type"])
        except RuntimeError:
            type_ = "Any"
            param = None
        if type_ != "Any":
            if "i." in type_:
                type_ = add_dict_type(type_)  # interfaces can be given as dicts
            type_ = add_not_set(type_)
        required = "(required) " if arg["required"] else ""
        doc = wrapped_doc(
            f":arg {arg['name']}: {required}{arg.get('description', 'No documentation available.')}",
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
        return arg, param

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
                "required": bool
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
        k["docstring"] = wrapped_doc(p.get("description"))
        kind = p["type"]["kind"]
        if kind == "instance_of":
            namespace = p["type"]["type"]["namespace"]
            name = p["type"]["type"]["name"]
            if f"{namespace}:{name}" in TYPE_REPLACEMENTS:
                namespace, name = TYPE_REPLACEMENTS[f"{namespace}:{name}"].split(":")
            instance = schema.find_type(name, namespace)
            if instance["kind"] == "interface":
                k["args"] = []
                k["params"] = []
                for arg in instance["properties"]:
                    python_arg, param = self.get_attribute_data(arg)
                    if python_arg["required"]:
                        # insert in the right place so that all required arguments
                        # appear at the top of the argument list
                        i = 0
                        for i in range(len(k["args"])):
                            if k["args"][i]["required"] is False:
                                break
                        k["args"].insert(i, python_arg)
                    else:
                        k["args"].append(python_arg)
                    if param:
                        k["params"].append(param)
            else:
                raise RuntimeError(
                    f"Cannot generate code for instances of kind '{instance['kind']}'"
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
                        },
                        {
                            "name": "_value",
                            "type": add_not_set(add_dict_type(value_type)),
                            "doc": [":arg _value: The query value for the field."],
                            "required": False,
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
                "required": bool
            ],
        }
        ```
        """
        type_ = schema.find_type(interface)
        if type_["kind"] != "interface":
            raise RuntimeError(f"Type {interface} is not an interface")
        if "inherits" in type_ and "type" in type_["inherits"]:
            # this class has parents, make sure we have all the parents in our
            # list of interfaces to render
            parent = type_["inherits"]["type"]["name"]
            base = type_
            while base and "inherits" in base and "type" in base["inherits"]:
                if base["inherits"]["type"]["name"] not in interfaces:
                    interfaces.append(base["inherits"]["type"]["name"])
                base = schema.find_type(
                    base["inherits"]["type"]["name"],
                    base["inherits"]["type"]["namespace"],
                )
        else:
            # no parent, will inherit from AttrDict
            parent = None
        k = {"name": interface, "parent": parent, "args": []}
        for arg in type_["properties"]:
            arg_type, _ = schema.get_attribute_data(arg)
            k["args"].append(arg_type)
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


def generate_interfaces_py(schema, filename):
    """Generate interfaces.py"""
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
        try:
            classes_list.index(k)
            continue
        except ValueError:
            pass
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
        f.write(interfaces_py.render(classes=classes_list))
    print(f"Generated {filename}.")


if __name__ == "__main__":
    schema = ElasticsearchSchema()
    generate_query_py(schema, "elasticsearch_dsl/query.py")
    generate_interfaces_py(schema, "elasticsearch_dsl/interfaces.py")
