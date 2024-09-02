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

RESERVED = {"from": "from_"}


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
        self.interfaces = set()

    def find_type(self, name, namespace=None):
        for t in self.schema["types"]:
            if t["name"]["name"] == name and (
                namespace is None or t["name"]["namespace"] == namespace
            ):
                return t

    def reset_interfaces(self):
        self.interfaces = set()

    def get_python_type(self, schema_type):
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
                    return self.get_python_type(
                        self.find_type(type_name["name"], type_name["namespace"])
                    )
            elif (
                type_name["namespace"] == "_types.query_dsl"
                and type_name["name"] == "QueryContainer"
            ):
                return "Query", {"type": "query"}
            else:
                type_ = self.find_type(type_name["name"], type_name["namespace"])
                if type_:
                    return self.get_python_type(type_)

        elif schema_type["kind"] == "type_alias":
            return self.get_python_type(schema_type["type"])

        elif schema_type["kind"] == "array_of":
            type_, param = self.get_python_type(schema_type["value"])
            if type_.startswith("Union["):
                types = type_[6:-1].split(",")
            return f"List[{type_}]", {**param, "multi": True} if param else None

        elif schema_type["kind"] == "dictionary_of":
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
            ):
                self.interfaces.add("PipeSeparatedFlags")
                return '"i.PipeSeparatedFlags"', None
            else:
                types = list(
                    dict.fromkeys(
                        [self.get_python_type(t) for t in schema_type["items"]]
                    )
                )
                return "Union[" + ", ".join([type_ for type_, _ in types]) + "]", None

        elif schema_type["kind"] == "enum":
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
                if schema_type["name"]["name"].endswith("RangeQuery"):
                    return '"wrappers.Range[Any]"', None
                elif schema_type["name"]["name"].endswith("ScoreFunction"):
                    name = schema_type["name"]["name"][:-8]
                    if name == "FieldValueFactorScore":
                        name = "FieldValueFactor"  # naming exception
                    return f'"f.{name}"', None
                elif schema_type["name"]["name"].endswith("DecayFunction"):
                    return '"f.DecayFunction"', None
                elif schema_type["name"]["name"].endswith("Function"):
                    return f"\"f.{schema_type['name']['name']}\"", None
            elif schema_type["name"]["namespace"] == "_types.analysis" and schema_type[
                "name"
            ]["name"].endswith("Analyzer"):
                return "str", None
            self.interfaces.add(schema_type["name"]["name"])
            return f"\"i.{schema_type['name']['name']}\"", None
        elif schema_type["kind"] == "user_defined_value":
            return "Any", None

        raise RuntimeError(f"Cannot find Python type for {schema_type}")

    def argument_to_python_type(self, arg):
        try:
            type_, param = schema.get_python_type(arg["type"])
        except RuntimeError:
            type_ = "Any"
            param = None
        if type_ != "Any":
            if "i." in type_:
                type_ = add_dict_type(type_)
            type_ = add_not_set(type_)
        required = "(required)" if arg["required"] else ""
        doc = wrapped_doc(
            f":arg {arg['name']}: {required}{arg.get('description', 'No documentation available.')}",
            subsequent_indent="    ",
        )
        kwarg = {
            "name": RESERVED.get(arg["name"], arg["name"]),
            "type": type_,
            "doc": doc,
            "required": arg["required"],
        }
        if param is not None:
            param = {"name": arg["name"], "param": param}
        return kwarg, param

    def instance_of_to_python_class(self, p, k):
        instance = schema.find_type(
            p["type"]["type"]["name"], p["type"]["type"]["namespace"]
        )
        if instance["kind"] == "interface":
            k["kwargs"] = []
            k["params"] = []
            for p in instance["properties"]:
                kwarg, param = self.argument_to_python_type(p)
                if kwarg["required"]:
                    i = 0
                    for i in range(len(k["kwargs"])):
                        if k["kwargs"][i]["required"] is False:
                            break
                    k["kwargs"].insert(i, kwarg)
                else:
                    k["kwargs"].append(kwarg)
                if param:
                    k["params"].append(param)
        elif instance["kind"] == "type_alias":
            if (
                "codegenNames" in instance
                and instance["type"]["kind"] == "union_of"
                and len(instance["type"]["items"]) == len(instance["codegenNames"])
            ):
                k["kwargs"] = []
                for name, type_ in zip(
                    instance["codegenNames"], instance["type"]["items"]
                ):
                    python_type, _ = self.get_python_type(type_)
                    k["kwargs"].append(
                        {
                            "name": name,
                            "type": f'Union[{python_type}, "NotSet"]',
                            "doc": [
                                f":arg {name}: An instance of ``{python_type[3:-1]}``."
                            ],
                            "required": False,
                        }
                    )
                    k["has_type_alias"] = True
            else:
                raise RuntimeError("Cannot generate code for non-enum type aliases")
        else:
            raise RuntimeError(
                f"Cannot generate code for instances of kind '{instance['kind']}'"
            )
        return k

    def dictionary_of_to_python_class(self, p, k):
        key_type, _ = schema.get_python_type(p["type"]["key"])
        if "InstrumentedField" in key_type:
            value_type, _ = schema.get_python_type(p["type"]["value"])
            if p["type"]["singleKey"]:
                k["kwargs"] = [
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
                k["has_field"] = True
            else:
                k["kwargs"] = [
                    {
                        "name": "_fields",
                        "type": f"Optional[Mapping[{key_type}, {value_type}]]",
                        "doc": [
                            ":arg _fields: A dictionary of fields with their values."
                        ],
                        "required": False,
                    },
                ]
                k["has_fields"] = True
        else:
            raise RuntimeError(f"Cannot generate code for type {p['type']}")
        return k

    def property_to_python_class(self, p):
        k = {"schema": p, "name": "".join([w.title() for w in p["name"].split("_")])}
        k["docstring"] = wrapped_doc(p.get("description"))
        kind = p["type"]["kind"]
        if kind == "instance_of":
            k = self.instance_of_to_python_class(p, k)
        elif kind == "dictionary_of":
            k = self.dictionary_of_to_python_class(p, k)
        else:
            raise RuntimeError(f"Cannot generate code for type {p['type']}")
        return k

    def interface_to_python_class(self, interface, interfaces):
        type_ = schema.find_type(interface)
        if type_["kind"] != "interface":
            raise RuntimeError(f"Type {interface} is not an interface")
        if "inherits" in type_ and "type" in type_["inherits"]:
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
            parent = None
        k = {"name": interface, "parent": parent, "properties": []}
        for arg in type_["properties"]:
            arg_type, _ = schema.argument_to_python_type(arg)
            k["properties"].append(arg_type)
        return k


def generate_query_classes(schema, filename):
    classes = []
    query_container = schema.find_type("QueryContainer", "_types.query_dsl")
    for p in query_container["properties"]:
        k = schema.property_to_python_class(p)
        classes.append(k)

    with open(filename, "wt") as f:
        f.write(
            query_py.render(
                classes=classes, parent="Query", interfaces=sorted(schema.interfaces)
            )
        )
    print(f"Generated {filename}.")


def generate_interfaces(schema, interfaces, filename):
    classes = {}
    for interface in interfaces:
        if interface == "PipeSeparatedFlags":
            continue  # handled as a special case
        schema.reset_interfaces()
        k = schema.interface_to_python_class(interface, interfaces)
        for new_interface in schema.interfaces:
            if new_interface not in interfaces:
                interfaces.append(new_interface)
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
    generate_query_classes(schema, "elasticsearch_dsl/query.py")
    interfaces = schema.interfaces
    generate_interfaces(schema, list(interfaces), "elasticsearch_dsl/interfaces.py")
