{% for k in classes %}
class {{ k.name }}({{ parent }}):
    """
    {% for line in k.docstring %}
    {{ line }}
    {% endfor %}
    {% if k.kwargs %}

    {% for kwarg in k.kwargs %}
    {% for line in kwarg.doc %}
    {{ line }}
    {% endfor %}
    {% endfor %}
    {% endif %}
    """
    name = "{{ k.schema.name }}"
    {% if k.params %}
    _param_defs = {
        {% for param in k.params %}
        "{{ param.name }}": {{ param.param }},
        {% endfor %}
        {% if k.name == "FunctionScore" %}
        "filter": {"type": "query"},
        "functions": {"type": "score_function", "multi": True},
        {% endif %}
    }
    {% endif %}

    def __init__(
        self,
        {% if k.kwargs and not k.has_field and not k.has_fields %}
        *,
        {% endif %}
        {% for kwarg in k.kwargs %}
        {{ kwarg.name }}: {{ kwarg.type }} = NOT_SET,
        {% endfor %}
        **kwargs: Any
    ):
        {% if k.name == "FunctionScore" %}
        if functions == NOT_SET:
            functions = []
            for name in ScoreFunction._classes:
                if name in kwargs:
                    functions.append({name: kwargs.pop(name)})
        {% elif k.has_field %}
        if _field != NOT_SET:
            kwargs[str(_field)] = _value
        {% elif k.has_fields %}
        if fields != NOT_SET:
            for field, value in _fields.items():
                kwargs[str(field)] = value
        {% elif k.has_type_alias %}
        {% for kwarg in k.kwargs %}
        {% if loop.index == 1 %}
        if {{ kwarg.name }} != NOT_SET:
        {% else %}
        elif {{ kwarg.name }} != NOT_SET:
        {% endif %}
            kwargs = {{ kwarg.name }}
        {% endfor %}
        {% endif %}
        super().__init__(
            {% if not k.has_field and not k.has_fields and not k.has_type_alias %}
            {% for kwarg in k.kwargs %}
            {{ kwarg.name }}={{ kwarg.name }},
            {% endfor %}
            {% endif %}
            **kwargs
        )

    {% if k.name == "MatchAll" %}
    def __add__(self, other: "Query") -> "Query":
        return other._clone()

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: "Query") -> "MatchAll":
        return self

    __ror__ = __or__

    def __invert__(self) -> "MatchNone":
        return MatchNone()


EMPTY_QUERY = MatchAll()

    {% elif k.name == "MatchNone" %}
    def __add__(self, other: "Query") -> "MatchNone":
        return self

    __and__ = __rand__ = __radd__ = __add__

    def __or__(self, other: "Query") -> "Query":
        return other._clone()

    __ror__ = __or__

    def __invert__(self) -> MatchAll:
        return MatchAll()

    {% elif k.name == "Bool" %}
    def __add__(self, other: Query) -> "Bool":
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.should += other.should
            q.must_not += other.must_not
            q.filter += other.filter
        else:
            q.must.append(other)
        return q

    __radd__ = __add__

    def __or__(self, other: Query) -> Query:
        for q in (self, other):
            if isinstance(q, Bool) and not any(
                (q.must, q.must_not, q.filter, getattr(q, "minimum_should_match", None))
            ):
                other = self if q is other else other
                q = q._clone()
                if isinstance(other, Bool) and not any(
                    (
                        other.must,
                        other.must_not,
                        other.filter,
                        getattr(other, "minimum_should_match", None),
                    )
                ):
                    q.should.extend(other.should)
                else:
                    q.should.append(other)
                return q

        return Bool(should=[self, other])

    __ror__ = __or__

    @property
    def _min_should_match(self) -> int:
        return getattr(
            self,
            "minimum_should_match",
            0 if not self.should or (self.must or self.filter) else 1,
        )

    def __invert__(self) -> Query:
        # Because an empty Bool query is treated like
        # MatchAll the inverse should be MatchNone
        if not any(chain(self.must, self.filter, self.should, self.must_not)):
            return MatchNone()

        negations: List[Query] = []
        for q in chain(self.must, self.filter):
            negations.append(~q)

        for q in self.must_not:
            negations.append(q)

        if self.should and self._min_should_match:
            negations.append(Bool(must_not=self.should[:]))

        if len(negations) == 1:
            return negations[0]
        return Bool(should=negations)

    def __and__(self, other: Query) -> Query:
        q = self._clone()
        if isinstance(other, Bool):
            q.must += other.must
            q.must_not += other.must_not
            q.filter += other.filter
            q.should = []

            # reset minimum_should_match as it will get calculated below
            if "minimum_should_match" in q._params:
                del q._params["minimum_should_match"]

            for qx in (self, other):
                min_should_match = qx._min_should_match
                # TODO: percentages or negative numbers will fail here
                # for now we report an error
                if not isinstance(min_should_match, int) or min_should_match < 0:
                    raise ValueError(
                        "Can only combine queries with positive integer values for minimum_should_match"
                    )
                # all subqueries are required
                if len(qx.should) <= min_should_match:
                    q.must.extend(qx.should)
                # not all of them are required, use it and remember min_should_match
                elif not q.should:
                    q.minimum_should_match = min_should_match
                    q.should = qx.should
                # all queries are optional, just extend should
                elif q._min_should_match == 0 and min_should_match == 0:
                    q.should.extend(qx.should)
                # not all are required, add a should list to the must with proper min_should_match
                else:
                    q.must.append(
                        Bool(should=qx.should, minimum_should_match=min_should_match)
                    )
        else:
            if not (q.must or q.filter) and q.should:
                q._params.setdefault("minimum_should_match", 1)
            q.must.append(other)
        return q

    __rand__ = __and__
    
    {% elif k.name == "Terms" %}
    def _setattr(self, name: str, value: Any) -> None:
        super()._setattr(name, list(value))

    {% endif %}

{% endfor %}
