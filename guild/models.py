"""The core Character model.

Three separate TODOs live in this file, for three different days — read
the notes at each one carefully, they're not all unlocked at the same time:

  - Day 1: Character's dunder methods (__repr__, __eq__, __hash__, __lt__,
    __bool__) — same idea as Item in items.py, applied to a class other
    exercises will already be using.
  - Day 4: HealerMixin / TankMixin / LoggableMixin — the mixin & MRO
    workshop.
  - Day 5: GuildMeta — the registry metaclass. Character does NOT use it
    yet (see the class statement below) — wiring it in is literally your
    last Day 5 step, once GuildMeta itself works.

fields.py (StringField/IntField) is already working, so Character's
fields below will validate correctly from Day 1 onward regardless of
which of the above TODOs you've reached.
"""

from __future__ import annotations

from typing import Dict, Type

from .fields import IntField, StringField


class GuildMeta(type):
    """TODO (Day 5): a metaclass that automatically registers every
    concrete Character subclass by name — direct analogue of how Odoo's
    ORM collects model classes into its model registry at class-creation
    time, not at instantiation time.

    Two things your __new__ needs to do, after creating the class via
    super().__new__(...):
      1. Skip registration for the base Character class itself (it has no
         `bases`, i.e. `bases == ()`).
      2. For every other (concrete) subclass: validate that it has an int
         `base_hp` class attribute (directly or inherited) — raise
         TypeError if not — then add it to `GuildMeta.registry` keyed by
         class name.

    Once this works, go to the bottom of this file and change
    `class Character:` to `class Character(metaclass=GuildMeta):` — the
    registry is useless to Character until that line changes.
    """

    registry: Dict[str, Type["Character"]] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        raise NotImplementedError("TODO (Day 5): implement GuildMeta.__new__")


# TODO (Day 5, last step): once GuildMeta works, change the line below to:
#     class Character(metaclass=GuildMeta):
class Character:
    """Base class for every playable character."""

    name = StringField(max_length=50)
    hp = IntField(minimum=0)
    level = IntField(minimum=1, maximum=100)

    base_hp: int = 10  # overridden by every concrete subclass

    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.hp = self.base_hp * level

    def describe_role(self) -> str:
        return "Adventurer"

    # --- Day 1 dunder set -------------------------------------------------

    def __repr__(self) -> str:
        """This will return a reconstructable string version of the Character
        Warrior(name='Grom', level=2, hp=30)
        """
        return f"{type(self).__name__}(name={self.name!r}, level={self.level}, hp={self.hp})"

    def __str__(self) -> str:
        """This return an user-friendly string representation of the character.
        Grom the Warrior (Lv.2, 30 HP)
        """
        return f"{self.name} the {type(self).__name__} (Lv.{self.level}, {self.hp} HP)"

    def __eq__(self, other: object) -> bool:
        """
        This will compare if two objects have the same concrete type, same name AND the same level.
        """
        if isinstance(other, Character):  # Ensures we are comparing Characters
            return (
                type(other) == type(self)
                and self.name == other.name
                and self.level == other.level
            )
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.hp, self.level))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return NotImplemented
        else:
            return self.level < other.level

    def __bool__(self) -> bool:
        return self.hp > 0


class Warrior(Character):
    base_hp = 15

    def describe_role(self) -> str:
        return "Warrior"


class Mage(Character):
    base_hp = 8

    def describe_role(self) -> str:
        return "Mage"


class Rogue(Character):
    base_hp = 10

    def describe_role(self) -> str:
        return "Rogue"


# --- Day 4 mixins: horizontal reuse without deep inheritance ---------------


class HealerMixin:
    """TODO (Day 4, Dev A/whoever owns this): adds healing behavior.

    describe_role() must call super().describe_role() and append
    " + Healer" to whatever it returns — this is deliberate: it's one
    half of the cooperative MRO chain exercised by Paladin below. Do not
    hard-code a return value; the whole point breaks if you do.

    heal(target, amount=None): heals `target` by `amount` (or by
    self.heal_power if amount is None), capped at target's max HP
    (target.base_hp * target.level). Returns the target's new hp.
    """

    heal_power: int = 5

    def describe_role(self) -> str:
        raise NotImplementedError("TODO (Day 4): implement HealerMixin.describe_role")

    def heal(self, target: "Character", amount: int = None) -> int:
        raise NotImplementedError("TODO (Day 4): implement HealerMixin.heal")


class TankMixin:
    """TODO (Day 4): adds taunt/aggro behavior.

    describe_role() must call super().describe_role() and append
    " + Tank" — same cooperative-chain requirement as HealerMixin above.

    taunt(enemies): for this exercise, a simplified placeholder is fine —
    e.g. just return list(enemies). The mechanism (MRO), not combat
    balance, is the point.
    """

    taunt_radius: int = 3

    def describe_role(self) -> str:
        return super().describe_role() + " + Tank"

    def taunt(self, enemies) -> list:
        return list(enemies)


class Paladin(HealerMixin, TankMixin, Warrior):
    """The deliberate mixin conflict. Once HealerMixin and TankMixin are
    implemented above, run Paladin.__mro__ and Paladin("x").describe_role()
    and be ready to explain, step by step, why the result is what it is —
    and what would change if TankMixin were listed before HealerMixin in
    the class statement above.
    """

    base_hp = 20


# --- Day 4 (independent mixin, not part of the conflict above) ------------


class LoggableMixin:
    """TODO (Day 4, other dev): logs every attribute assignment on the
    instance into self._log (a list of strings).

    Two things to get right:
      1. __init__ needs to set up self._log = [] BEFORE calling
         super().__init__(...), and must do so via self.__dict__ directly
         (not `self._log = []`) to avoid triggering your own __setattr__
         override recursively before _log exists.
      2. __setattr__ should append an entry (e.g. f"{name} = {value!r}")
         for every assignment except to _log itself, then still actually
         perform the assignment via super().__setattr__(...).

    `log` should be a read-only property returning a copy of the list
    (not the live list itself).
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.__init__")

    def __setattr__(self, name: str, value) -> None:
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.__setattr__")

    @property
    def log(self) -> list:
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.log")


class LoggedMage(LoggableMixin, Mage):
    """Demo combination used by the test suite / workshop walkthrough."""
