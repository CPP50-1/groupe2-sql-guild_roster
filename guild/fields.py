"""Descriptors used as typed, validated class attributes.

Field / Validated / StringField / IntField below are PROVIDED, WORKING —
Character depends on them from Day 1 onward, so the mechanism can't be a
blank TODO without breaking every earlier day's tests.

Read this file closely anyway — this is the "spot it" checkpoint moment
made concrete: Odoo's own fields.Char / fields.Integer are descriptors in
exactly this sense (a data descriptor with __get__/__set__), and this is a
from-scratch version of that same mechanism.

--------------------------------------------------------------------------
YOUR DAY 4 TODO: add a new `FloatField` class below, following the same
pattern as IntField. It should:
  - accept `required`, `minimum`, `maximum` (same as IntField)
  - validate that the value is a float OR an int (reject strings, etc.)
  - raise the same exceptions (RequiredFieldError / TypeMismatchError /
    RangeError) that Validated already raises for the other field types
--------------------------------------------------------------------------
"""

from __future__ import annotations

from typing import Any, Optional, Type


class Field:
    """Base descriptor: a data descriptor (defines both __get__ and __set__,
    so it always takes priority over instance __dict__ entries, this is
    what makes it a *data* descriptor rather than a non-data one).
    """

    def __set_name__(self, owner: Type, name: str) -> None:
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: Any, owner: Type) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self.private_name)

    def __set__(self, instance: Any, value: Any) -> None:
        self.validate(value)
        instance.__dict__[self.private_name] = value

    def __delete__(self, instance: Any) -> None:
        instance.__dict__.pop(self.private_name, None)

    def validate(self, value: Any) -> None:
        """Subclasses override this to add type/range checks."""


class Validated(Field):
    """A descriptor that type-checks (and optionally range-checks) any
    value assigned to it.
    """

    def __init__(
        self,
        expected_type: Type,
        required: bool = True,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ):
        self.expected_type = expected_type
        self.required = required
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> None:
        if value is None:
            if self.required:
                raise RequiredFieldError(self.name)
            return
        if not isinstance(value, self.expected_type):
            raise TypeMismatchError(self.name, self.expected_type, value)
        if self.minimum is not None and value < self.minimum:
            raise RangeError(
                self.name, value, minimum=self.minimum, maximum=self.maximum
            )
        if self.maximum is not None and value > self.maximum:
            raise RangeError(
                self.name, value, minimum=self.minimum, maximum=self.maximum
            )


class StringField(Validated):
    """A Validated shortcut for non-empty strings."""

    def __init__(self, required: bool = True, max_length: Optional[int] = None):
        super().__init__(expected_type=str, required=required)
        self.max_length = max_length

    def validate(self, value: Any) -> None:
        super().validate(value)
        if (
            value is not None
            and self.max_length is not None
            and len(value) > self.max_length
        ):
            raise RangeError(self.name, value, maximum=self.max_length)
        if value is not None and value.strip() == "" and self.required:
            raise RequiredFieldError(self.name)


class IntField(Validated):
    """A Validated shortcut for integers, with optional min/max bounds."""

    def __init__(
        self,
        required: bool = True,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None,
    ):
        super().__init__(
            expected_type=int, required=required, minimum=minimum, maximum=maximum
        )


class FloatField(Validated):
    """A Validated shortcut for floats (accepts int too, since int is
    float-ish in Python).
    """

    def __init__(
        self,
        required: bool = True,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ):
        super().__init__(
            expected_type=float, required=required, minimum=minimum, maximum=maximum
        )

    def validate(self, value):
        if value is None:
            if self.required:
                raise ValueError(f"'{self.name}' is required and cannot be None")
            return
        if not isinstance(value, (float, int)):
            raise TypeError(
                f"'{self.name}' expected float, got {type(value).__name__} ({value!r})"
            )
        if self.minimum is not None and value < self.minimum:
            raise ValueError(
                f"'{self.name}' must be >= {self.minimum} and <= {self.maximum}, got {value!r}"
            )
        if self.maximum is not None and value > self.maximum:
            raise ValueError(
                f"'{self.name}' must be >= {self.minimum} and <= {self.maximum}, got {value!r}"
            )
