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
        """TODO (Day 2): add item, no-op if it's already present."""
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.add")

    def discard(self, item: Any) -> None:
        """TODO (Day 2): remove item if present; do nothing if it isn't."""
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.discard")

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__contains__")

    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__iter__")

    def __len__(self) -> int:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__len__")

    def __repr__(self) -> str:
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__repr__")

    def __eq__(self, other: object) -> bool:
        """TODO (Day 2): two OrderedSets are equal if they contain the
        same items in the same order.
        """
        raise NotImplementedError("TODO (Day 2): implement OrderedSet.__eq__")


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
        """TODO (Day 2): an iterator must be iterable (return itself)."""
        raise NotImplementedError("TODO (Day 2): implement RosterIterator.__iter__")

    def __next__(self) -> Character:
        """TODO (Day 2): return the next character, advance the index,
        raise StopIteration once you've gone past the end.
        """
        raise NotImplementedError("TODO (Day 2): implement RosterIterator.__next__")


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

        raise NotImplementedError("TODO (Day 2): implement what to do if index is out of range.")

    def __setitem__(self, index: int, value: Character) -> None:
        if not isinstance(value, Character):
            raise TypeError("Wrong type for Roster.__setitem__. 'value' should be a Character.")

        if 0 <= index < len(self._characters):
            self._characters[index] = value
            return

        raise NotImplementedError("TODO (Day 2): implement what to do if index is out of range.")

    def __delitem__(self, index: int) -> None:
        if 0 <= index < len(self._characters):
            self._characters.pop(index)
            return

        raise NotImplementedError("TODO (Day 2): implement what to do if index is out of range.")

    def __contains__(self, item: Character) -> bool:
        return item in self._characters

    def __len__(self) -> int:
        return len(self._characters)

    def __iter__(self) -> RosterIterator:
        return iter(self._characters)

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
