"""Day 2 workshop targets, one per developer:

    Dev A -> OrderedSet      (custom unique-item structure)
    Dev B -> StatCalculator  (memoized callable, state held between calls)
    Dev C -> Roster          (full container protocol + iterator protocol
                              from scratch, i.e. __iter__ returning a real
                              iterator object with __next__, not a generator)

Constructors that just store their arguments are given; the actual
protocol methods are TODOs.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List

from .models import Character


# --- Dev A: OrderedSet ------------------------------------------------------


class OrderedSet:
    """A set that remembers insertion order. Backed by a dict (Python 3.7+
    dicts are insertion-ordered) purely for its keys — this is what gives
    O(1) membership instead of the O(n) a list would need. Use only the
    keys of self._data; never store meaningful values in them.
    """

    def __init__(self, items: Iterator[Any] = ()):
        self._data: Dict[Any, None] = {}
        for item in items:
            self.add(item)

    def add(self, item: Any) -> None:
        self._data[item] = None

    def discard(self, item: Any) -> None:
        self._data.pop(item, None)

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, OrderedSet) and self._data == other._data

    def __or__(self, other: Any) -> OrderedSet:
        if not isinstance(other, OrderedSet):
            return NotImplemented
        new_items = list(self) + \
            [item for item in other if item not in self._data]
        return self.__class__(new_items)

    def __and__(self, other: Any) -> OrderedSet:
        if not isinstance(other, OrderedSet):
            return NotImplemented
        other_set = set(other)
        new_items = [item for item in self if item in other_set]
        return self.__class__(new_items)

    def __sub__(self, other: Any) -> OrderedSet:
        if not isinstance(other, OrderedSet):
            return NotImplemented
        other_set = set(other)
        new_items = [item for item in self if item not in other_set]
        return self.__class__(new_items)


# --- Dev B: memoized callable ------------------------------------------------


class StatCalculator:
    """A callable object that caches results by argument, for an
    expensive/derived stat computation.
    """

    def __init__(self):
        self._cache: Dict[tuple, int] = {}
        self.calls = 0
        self.cache_hits = 0

    def __call__(self, character: Character, difficulty: int) -> int:
        self.calls += 1

        key = (type(character).__name__, character.level, difficulty)

        if key in self._cache:
            self.cache_hits += 1
            return self._cache[key]

        result = (character.level * 7 + difficulty * 13) % 100
        self._cache[key] = result
        return result


# --- Dev C: full container protocol + iterator protocol from scratch -------


class RosterIterator:
    """A standalone iterator object for Roster, built from scratch rather
    than via a generator function — this is what Day 2's "__iter__ and
    __next__ from scratch" specifically asks for.
    """

    def __init__(self, characters: List[Character]):
        self._characters = characters
        self._index = 0

    def __iter__(self) -> "RosterIterator":
        return self

    def __next__(self) -> Character:
        """ return the next character, advance the index,
        raise StopIteration once you've gone past the end.
        """
        try:
            c = self._characters[self._index]
            self._index += 1
            return c
        except IndexError:
            raise StopIteration


class Roster:
    """A guild's roster of characters, supporting the full container
    protocol: indexing, assignment, deletion, membership, length, and
    iteration.
    """

    def __init__(self, characters: Iterator[Character] = ()):
        self._characters: List[Character] = list(characters)

    def __getitem__(self, index: int) -> Character:
        if 0<= index < len(self._characters):
            return self._characters[index]

    def __setitem__(self, index: int, value: Character) -> None:
        if not isinstance(value, Character):
            raise TypeError("Wrong type for Roster.__setitem__. 'value' should be a Character.")

        if 0 <= index < len(self._characters):
            self._characters[index] = value
            return

    def __delitem__(self, index: int) -> None:
        if 0 <= index < len(self._characters):
            self._characters.pop(index)
            return

    def __contains__(self, item: Character) -> bool:
        return item in self._characters

    def __len__(self) -> int:
        return len(self._characters)

    def __iter__(self) -> RosterIterator:
        return RosterIterator(self._characters)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(characters={self._characters})"

    def add(self, character: Character) -> None:
        self._characters.append(character)

    def alive_characters(self) -> Iterator[Character]:
        for character in self._characters:
            if character.hp > 0:
                yield character

    def sorted_by_level(self) -> List[Character]:
        return sorted(self._characters)
