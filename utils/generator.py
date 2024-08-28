from elasticsearch_dsl import VERSION
import json
import textwrap
from urllib.request import urlopen
from urllib.error import HTTPError
from jinja2 import Environment, PackageLoader, select_autoescape

jinja_env = Environment(
    loader=PackageLoader("utils"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)
query_py = jinja_env.get_template("query.py.tpl")
interfaces_py = jinja_env.get_template("interfaces.py.tpl")


def wrapped_doc(text, width=70, initial_indent="", subsequent_indent=""):
    """Formats a docstring as a list of lines of up to the request width."""
    return textwrap.wrap(
        (text or "No documentation available.").replace("\n", " "),
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
    )


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
            return f"List[{type_}]", None

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
                return f"Union[{type_}, List[{type_}]]", (
                    {"type": param["type"], "multi": True} if param else None
                )
            elif (
                len(schema_type["items"]) == 2
                and schema_type["items"][0]["kind"] == "instance_of"
                and schema_type["items"][1]["kind"] == "instance_of"
                and schema_type["items"][0]["type"]
                == {"name": "T", "namespace": "_spec_utils.PipeSeparatedFlags"}
            ):
                self.interfaces.add("PipeSeparatedFlags")
                return '"PipeSeparatedFlags"', None
            else:
                types = [self.get_python_type(t) for t in schema_type["items"]]
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
                    return '"wrappers.Range"', None
                elif schema_type["name"]["name"].endswith("Function"):
                    return f"\"function.{schema_type['name']['name']}\"", None
            elif schema_type["name"]["namespace"] == "_types.analysis" and schema_type[
                "name"
            ]["name"].endswith("Analyzer"):
                return f"\"analysis.{schema_type['name']['name']}\"", None
            self.interfaces.add(schema_type["name"]["name"])
            return f"\"i.{schema_type['name']['name']}\"", None
        elif schema_type["kind"] == "user_defined_value":
            return "Any", None

        raise RuntimeError(f"Cannot find Python type for {schema_type}")


def generate_query_classes(schema, filename):
    classes = []
    query_container = schema.find_type("QueryContainer", "_types.query_dsl")
    for p in query_container["properties"]:
        k = {"schema": p, "name": "".join([w.title() for w in p["name"].split("_")])}
        k["docstring"] = wrapped_doc(p.get("description"))
        kind = p["type"]["kind"]
        if kind == "instance_of":
            instance = schema.find_type(
                p["type"]["type"]["name"], p["type"]["type"]["namespace"]
            )
            if instance["kind"] == "interface":
                k["kwargs"] = []
                k["params"] = []
                for arg in instance["properties"]:
                    type_, param = schema.get_python_type(arg["type"])
                    if arg["required"] is False and type_ != "Any":
                        type_ = add_not_set(type_)
                    doc = wrapped_doc(
                        f":arg {arg['name']}: {arg.get('description')}",
                        subsequent_indent="    ",
                    )
                    if arg["required"] is False:
                        k["kwargs"].append(
                            {
                                "name": arg["name"],
                                "type": type_,
                                "doc": doc,
                                "required": False,
                            }
                        )
                    else:
                        i = 0
                        for i in range(len(k["kwargs"])):
                            if k["kwargs"][i]["required"] is False:
                                break
                        k["kwargs"].insert(
                            i,
                            {
                                "name": arg["name"],
                                "type": type_,
                                "doc": doc,
                                "required": True,
                            },
                        )
                    if param is not None:
                        k["params"].append({"name": arg["name"], "param": param})

        elif kind == "dictionary_of":
            key_type, _ = schema.get_python_type(p["type"]["key"])
            if "InstrumentedField" in key_type:
                value_type, _ = schema.get_python_type(p["type"]["value"])
                if p["type"]["singleKey"]:
                    k["kwargs"] = [
                        {
                            "name": "field",
                            "type": add_not_set(key_type),
                            "doc": [":arg field: Field to use"],
                            "required": False,
                        },
                        {
                            "name": "value",
                            "type": add_not_set(value_type),
                            "doc": [":arg value: Field value"],
                            "required": False,
                        },
                    ]
                    k["has_field"] = True
                else:
                    k["kwargs"] = [
                        {
                            "name": "fields",
                            "type": f"Optional[Mapping[{key_type}, {value_type}]]",
                            "doc": [
                                ":arg fields: A dictionary of fields with their values."
                            ],
                            "required": False,
                        },
                    ]
                    k["has_fields"] = True
            else:
                raise RuntimeError(f"Cannot generate code for type {p['type']}")

        else:
            raise RuntimeError(f"Cannot generate code for type {p['type']}")
        classes.append(k)

    with open(filename, "wt") as f:
        f.write(
            query_py.render(
                classes=classes, parent="Query", interfaces=sorted(schema.interfaces)
            )
        )


def generate_interfaces(schema, interfaces, filename):
    classes = {}
    for interface in interfaces:
        if interface == "PipeSeparatedFlags":
            continue  # handled as a special case
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
        schema.reset_interfaces()
        for p in type_["properties"]:
            type_, param = schema.get_python_type(p["type"])
            k["properties"].append({"name": p["name"], "type": type_})
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


if __name__ == "__main__":
    schema = ElasticsearchSchema()
    generate_query_classes(schema, "elasticsearch_dsl/query.py")
    interfaces = schema.interfaces
    generate_interfaces(schema, list(interfaces), "elasticsearch_dsl/interfaces.py")
