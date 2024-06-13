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

from datetime import date, datetime
from fnmatch import fnmatch
from typing import TYPE_CHECKING, Any, Generic, List, Optional, TypeVar, Union, overload

from .exceptions import ValidationException
from .field import (
    Binary,
    Boolean,
    Date,
    Field,
    Float,
    InstrumentedField,
    Integer,
    Nested,
    Object,
    Text,
)
from .mapping import Mapping
from .utils import DOC_META_FIELDS, ObjectBase


class MetaField:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


class DocumentMeta(type):
    def __new__(cls, name, bases, attrs):
        # DocumentMeta filters attrs in place
        attrs["_doc_type"] = DocumentOptions(name, bases, attrs)
        return super().__new__(cls, name, bases, attrs)

    def __getattr__(cls, attr):
        if attr in cls._doc_type.mapping:
            return InstrumentedField(attr, cls._doc_type.mapping[attr])
        return super().__getattribute__(attr)


class DocumentOptions:
    type_annotation_map = {
        int: (Integer, {}),
        float: (Float, {}),
        bool: (Boolean, {}),
        str: (Text, {}),
        bytes: (Binary, {}),
        datetime: (Date, {}),
        date: (Date, {"format": "yyyy-MM-dd"}),
    }

    def __init__(self, name, bases, attrs):
        meta = attrs.pop("Meta", None)

        # create the mapping instance
        self.mapping = getattr(meta, "mapping", Mapping())

        # register the document's fields, which can be given in a few formats:
        #
        # class MyDocument(Document):
        #     # required field using native typing
        #     # (str, int, float, bool, datetime, date)
        #     field1: str
        #
        #     # optional field using native typing
        #     field2: Optional[datetime]
        #
        #     # array field using native typing
        #     field3: list[int]
        #
        #     # sub-object, same as Object(MyInnerDoc)
        #     field4: MyInnerDoc
        #
        #     # nested sub-objects, same as Nested(MyInnerDoc)
        #     field5: list[MyInnerDoc]
        #
        #     # use typing, but override with any stock or custom field
        #     field6: bool = MyCustomField()
        #
        #     # best mypy and pyright typing support
        #     field7: M[date]
        #     field8: M[str] = mapped_field(MyCustomText())
        #
        #     # legacy format without Python typing
        #     field8 = Text()
        annotations = attrs.get("__annotations__", {})
        fields = set([n for n in attrs if isinstance(attrs[n], Field)])
        fields.update(annotations.keys())
        for name in fields:
            if name in attrs:
                value = attrs[name]
            else:
                type_ = annotations[name]
                required = True
                multi = False
                while hasattr(type_, "__origin__"):
                    if type_.__origin__ == Mapped:
                        type_ = type_.__args__[0]
                    elif type_.__origin__ == Union:
                        if len(type_.__args__) == 2 and type_.__args__[1] is type(None):
                            required = False
                            type_ = type_.__args__[0]
                        else:
                            raise TypeError("Unsupported union")
                    elif type_.__origin__ in [list, List]:
                        multi = True
                        type_ = type_.__args__[0]
                    else:
                        break
                field_args = []
                field_kwargs = {}
                if not isinstance(type_, type):
                    raise TypeError(f"Cannot map type {type_}")
                elif issubclass(type_, InnerDoc):
                    field = Nested if multi else Object
                    field_args = [type_]
                elif type_ in self.type_annotation_map:
                    field, field_kwargs = self.type_annotation_map[type_]
                elif not issubclass(type_, Field):
                    raise TypeError(f"Cannot map type {type_}")
                else:
                    field = type_
                field_kwargs = {"multi": multi, "required": required, **field_kwargs}
                value = field(*field_args, **field_kwargs)
            self.mapping.field(name, value)
            if name in attrs:
                del attrs[name]

        # add all the mappings for meta fields
        for name in dir(meta):
            if isinstance(getattr(meta, name, None), MetaField):
                params = getattr(meta, name)
                self.mapping.meta(name, *params.args, **params.kwargs)

        # document inheritance - include the fields from parents' mappings
        for b in bases:
            if hasattr(b, "_doc_type") and hasattr(b._doc_type, "mapping"):
                self.mapping.update(b._doc_type.mapping, update_only=True)

    @property
    def name(self):
        return self.mapping.properties.name


_FieldType = TypeVar("_FieldType")


class Mapped(Generic[_FieldType]):
    __slots__ = {}

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: None, owner: Any) -> InstrumentedField: ...

        @overload
        def __get__(self, instance: object, owner: Any) -> _FieldType: ...

        def __get__(
            self, instance: Optional[object], owner: Any
        ) -> Union[InstrumentedField, _FieldType]: ...

        def __set__(self, instance: Optional[object], value: _FieldType) -> None: ...

        def __delete__(self, instance: Any) -> None: ...


M = Mapped


def mapped_field(field) -> Any:
    return field


class InnerDoc(ObjectBase, metaclass=DocumentMeta):
    """
    Common class for inner documents like Object or Nested
    """

    @classmethod
    def from_es(cls, data, data_only=False):
        if data_only:
            data = {"_source": data}
        return super().from_es(data)


class DocumentBase(ObjectBase):
    """
    Model-like class for persisting documents in elasticsearch.
    """

    @classmethod
    def _matches(cls, hit):
        if cls._index._name is None:
            return True
        return fnmatch(hit.get("_index", ""), cls._index._name)

    @classmethod
    def _get_using(cls, using=None):
        return using or cls._index._using

    @classmethod
    def _default_index(cls, index=None):
        return index or cls._index._name

    @classmethod
    def init(cls, index=None, using=None):
        """
        Create the index and populate the mappings in elasticsearch.
        """
        i = cls._index
        if index:
            i = i.clone(name=index)
        i.save(using=using)

    def _get_index(self, index=None, required=True):
        if index is None:
            index = getattr(self.meta, "index", None)
        if index is None:
            index = getattr(self._index, "_name", None)
        if index is None and required:
            raise ValidationException("No index")
        if index and "*" in index:
            raise ValidationException("You cannot write to a wildcard index.")
        return index

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{key}={getattr(self.meta, key)!r}"
                for key in ("index", "id")
                if key in self.meta
            ),
        )

    def to_dict(self, include_meta=False, skip_empty=True):
        """
        Serialize the instance into a dictionary so that it can be saved in elasticsearch.

        :arg include_meta: if set to ``True`` will include all the metadata
            (``_index``, ``_id`` etc). Otherwise just the document's
            data is serialized. This is useful when passing multiple instances into
            ``elasticsearch.helpers.bulk``.
        :arg skip_empty: if set to ``False`` will cause empty values (``None``,
            ``[]``, ``{}``) to be left on the document. Those values will be
            stripped out otherwise as they make no difference in elasticsearch.
        """
        d = super().to_dict(skip_empty=skip_empty)
        if not include_meta:
            return d

        meta = {"_" + k: self.meta[k] for k in DOC_META_FIELDS if k in self.meta}

        # in case of to_dict include the index unlike save/update/delete
        index = self._get_index(required=False)
        if index is not None:
            meta["_index"] = index

        meta["_source"] = d
        return meta
