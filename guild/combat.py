"""Day 3, Dev A: a turn-based combat coroutine.

Usage sketch once implemented:

    log = []
    fight = battle(character, log)
    state = next(fight)                # prime the generator
    state = fight.send("attack")       # player acts, generator advances
    state = fight.throw(AmbushError()) # simulate an interrupt mid-battle
    fight.close()                      # abandon the fight cleanly
"""

from __future__ import annotations

from typing import Dict, Generator, List
from unittest import case

from .exceptions import GuildError
from .models import Character, Warrior, Rogue


class AmbushError(GuildError):
    """Raised into the battle generator to simulate a mid-fight ambush —
    exercises Generator.throw() specifically.
    """

    """
    Requirements:
      - Append a "X appears!" style line to combat_log at the start.
      - Loop while both character_hp and enemy_hp are above 0. Each
        iteration: `action = yield {...state snapshot...}`, then handle
        action in ("attack", "heal", "flee") plus a fallback for unknown
        actions. "attack" reduces enemy_hp; "heal" restores some
        character_hp (capped at character.base_hp * character.level);
        "flee" should `return` immediately (ending the generator).
      - After a successful attack, if the enemy is still alive, it hits
        back (reduce character_hp by enemy_attack).
      - When the loop ends naturally (someone hit 0 hp), yield one final
        state dict with an "outcome" key ("victory" or "defeat").
      - Wrap the whole thing in try/except AmbushError: catching an
        ambush thrown in via .throw() should apply damage and yield a
        state dict with "ambushed": True.
      - Use `finally` to append a "Combat generator closed." line to
        combat_log — this must run whether the generator ends via
        `return`, naturally, or via .close() (which raises GeneratorExit
        at the suspended yield point). Do not `yield` from inside a
        finally block that's handling GeneratorExit — that will raise a
        RuntimeError.

    `combat_log` is a list supplied by the caller (not returned) because
    generator locals disappear once the frame ends — this is why the log
    needs to live outside the generator itself.
    """


def battle(
    character: Character,
    combat_log: List[str],
    enemy_name: str = "Goblin",
    enemy_hp: int = 30,
    enemy_attack: int = 5,
) -> Generator[Dict, str, None]:
    combat_log.append(f"{enemy_name} appears!")
    try:
        while character.hp > 0 and enemy_hp > 0:
            action = yield {
                "character": character,
                "combat_log": combat_log,
                "enemy_hp": enemy_hp,
            }

            match action:
                case "attack":
                    enemy_hp -= 10  # Scharacter.level
                    combat_log.append(
                        f"{character.name} hits {enemy_name}. {character.name}.hp = {character.hp}, {enemy_name}.hp = {enemy_hp}"
                    )
                    if enemy_hp > 0:
                        character.hp -= enemy_attack
                        combat_log.append(
                            f"{enemy_name} hits back {character.name}. {character.name}.hp = {character.hp}, {enemy_name}.hp = {enemy_hp}"
                        )
                case "heal":
                    cap = character.base_hp * character.level
                    character.hp = min(character.hp + character.level, cap)
                    combat_log.append(
                        f"{character.name} heals. {character.name}.hp = {character.hp}"
                    )
                case "flee":
                    combat_log.append(
                        f"{character.name} flees from {enemy_name}!")
                    return
                case _:
                    combat_log.append(
                        f"{character.name} hesitates, unsure what to do.")

        outcome = "victory" if enemy_hp <= 0 else "defeat"
        combat_log.append(f"Battle ends in {outcome} for {character.name}.")
        yield {
            "character": character,
            "combat_log": combat_log,
            "enemy_hp": enemy_hp,
            "outcome": outcome,
        }

    except AmbushError:
        character.hp -= enemy_attack
        combat_log.append(
            f"Ambush! {enemy_name} ambushes {character.name}! {character.name}.hp = {character.hp}"
        )
        yield {
            "character": character,
            "combat_log": combat_log,
            "enemy_hp": enemy_hp,
            "ambushed": True,
        }

    finally:
        combat_log.append("Combat generator closed.")
