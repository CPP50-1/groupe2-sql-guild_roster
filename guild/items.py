"""Day 1 shared build: a class with full comparison, equality, repr, and
set support — the "Money class" pattern (currency + amount) from the
program, adapted to the guild domain (an inventory item with a value and
a rarity tier).

Rarity and __init__ are given. Your job is the dunder methods below.
Remember the pairing rule: __eq__ and __hash__ must always be defined
together and stay consistent, or Item becomes unusable in sets/dicts.
"""

from __future__ import annotations

from functools import total_ordering
from enum import IntEnum


class Rarity(IntEnum):
    """IntEnum so rarities compare naturally (COMMON < RARE < LEGENDARY)
    without any extra work — this is used by Item.__lt__ below.
    """

    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@total_ordering
class Item:
    """An inventory item, ordered first by rarity then by value.

    @total_ordering fills in the remaining comparison operators once you
    provide __eq__ and __lt__ — you don't need to implement __le__/__gt__/
    __ge__ yourself.
    """

    def __init__(self, name: str, rarity: Rarity, value: int):
        self.name = name
        self.rarity = rarity
        self.value = value

    def __repr__(self) -> str:
        return (
            f"Item(name='{self.name}', rarity={self.rarity.name}, value={self.value})"
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.rarity.name.title()}, {self.value}g)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        else:
            return (
                self.name == other.name
                and self.rarity == other.rarity
                and self.value == other.value
            )

    def __hash__(self) -> int:
        """Must stay consistent with __eq__."""
        return hash((self.name, self.rarity, self.value))

    def __lt__(self, other: object) -> bool:
        """Order by rarity first, then value."""
        if not isinstance(other, Item):
            return NotImplemented
        return (self.rarity, self.value) < (other.rarity, other.value)

    def __bool__(self) -> bool:
        """Truthy if the item has any value."""
        return self.value != 0

    def __add__(self, other: Item) -> Item:
        if not isinstance(other, Item):
            return NotImplemented
        if self.name != other.name or self.rarity != other.rarity:
            raise TypeError()
        return Item(self.name, self.rarity, self.value + other.value)

    def __format__(self, format_spec: str) -> str:
        if format_spec == "short":
            return self.name
        elif format_spec == "full":
            return f"{self.name} ({self.rarity.name.title()}, {self.value})"
        else:
            return str(self)
