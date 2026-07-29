"""Day 3, Dev C: two pieces, both TODOs.

1. An infinite dungeon generator built from yield-from delegation to a
   per-floor sub-generator.
2. A contextlib.contextmanager-style transaction. Look at
   exceptions.batch_validation (in exceptions.py) first — it's a complete,
   working example of exactly this pattern (a generator wrapped in
   @contextmanager) — before writing this one from scratch.
"""

from __future__ import annotations

import random

from contextlib import contextmanager
from typing import Dict, Iterator, List


# --- TODO (Day 3): yield-from delegation + lazy infinite sequence ----------


def floor_encounters(floor_number: int, dungeon_log: List[str]) -> Iterator[Dict]:
    """TODO: one floor's worth of encounters.

    Requirements:
      - Append "Entering floor N" to dungeon_log at the start.
      - Build a small list of encounter dicts for this floor (a monster
        and a loot chest at minimum; add a trap every 3rd floor — your
        call on the exact shape, keep it consistent with dungeon_floors
        below and with the tests).
      - For each encounter: `action = yield encounter`. If action ==
        "retreat", append a log line and `return "retreated"` immediately.
      - If the loop finishes without a retreat, append a "cleared" log
        line and `return "cleared"`.
      - Wrap the body in try/finally, appending a "Leaving floor N" log
        line in the finally block — this needs to run whether the floor
        ends via retreat, via clearing it, or via the caller closing the
        whole dungeon mid-floor.
    """

    dungeon_log.append(f"Entering floor {floor_number}")

    bonus = int(floor_number / 1.5)
    monsters = 1 + random.randint(0, bonus)
    chests = 1 + random.randint(0, bonus)

    encounters = [{"type": "monster", "floor": floor_number}] * monsters + [
        {"type": "chest", "floor": floor_number}
    ] * chests
    if floor_number % 3 == 0:
        encounters.append({"type": "trap", "floor": floor_number})

    random.shuffle(encounters)

    try:
        for encounter in encounters:
            action = yield encounter
            if action == "retreat":
                dungeon_log.append("Party retreats mid-floor.")
                return "retreated"
        dungeon_log.append(f"Floor {floor_number} cleared.")
        return "cleared"
    finally:
        dungeon_log.append(f"Leaving floor {floor_number}")


def dungeon_floors(dungeon_log: List[str]) -> Iterator[Dict]:
    """TODO: an intentionally endless generator — there is no fixed last
    floor, only a floor the party chooses to stop at.

    Requirements:
      - Loop forever, incrementing a floor_number each iteration.
      - Delegate to floor_encounters via `yield from` — capture its
        return value (`result = yield from floor_encounters(...)`).
        This is what lets you find out *why* the floor ended (cleared vs.
        retreated) without any extra signalling mechanism — yield from
        forwards every .send() call through to the sub-generator AND
        surfaces its return value once it's exhausted.
      - If the result is "retreated", log a "returns to town" line and
        `return` (ending the whole dungeon run).
      - Wrap the while loop in try/finally, logging "Dungeon generator
        closed." in the finally block — reached both by the `return`
        above and by GeneratorExit (i.e. the caller calling .close()).
    """
    floor_number = 0
    try:
        while True:
            floor_number += 1
            result = yield from floor_encounters(floor_number, dungeon_log)
            if result == "retreated":
                dungeon_log.append("Party returns to town.")
                return
    finally:
        dungeon_log.append("Dungeon generator closed.")


# --- TODO (Day 3): guild treasury transaction --------------------------------


@contextmanager
def guild_transaction(treasury: Dict[str, int]) -> Iterator[Dict[str, int]]:
    """TODO: simulates a database transaction over an in-memory treasury
    dict — mutations inside the `with` block are kept if the block
    completes without error, and rolled back to the pre-block snapshot if
    it raises.

    Requirements:
      - Take a snapshot (a copy) of `treasury` before yielding it.
      - `yield treasury` so the caller can mutate it directly inside the
        `with` block.
      - If an exception occurs inside the block, restore `treasury` to
        the snapshot's contents, then re-raise the exception — do NOT
        suppress it. (Suppressing would mean *not* re-raising; that would
        be the wrong choice here, and worth being able to explain why.)
    """
    saved_treasury = treasury.copy()
    try:
        yield treasury
    except Exception:
        treasury.clear()
        treasury.update(saved_treasury)
        raise
