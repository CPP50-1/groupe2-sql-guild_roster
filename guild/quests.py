"""Day 3, Dev B: a quest pipeline built almost entirely from itertools.

The three quest-source generators below are given (they're just static
data). Everything that actually combines/filters/groups them using
itertools is a TODO.
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, Iterator, List

from .models import Character

Quest = Dict[str, object]


# --- Static quest sources, given -------------------------------------------

def daily_quests() -> Iterator[Quest]:
    yield {"name": "Clear the Rat Cellar", "reward_gold": 20, "min_level": 1}
    yield {"name": "Escort the Merchant", "reward_gold": 35, "min_level": 2}


def guild_quests() -> Iterator[Quest]:
    yield {"name": "Retrieve the Lost Banner", "reward_gold": 60, "min_level": 3}
    yield {"name": "Defend the Outpost", "reward_gold": 90, "min_level": 5}


def event_quests() -> Iterator[Quest]:
    yield {"name": "Harvest Festival Errand", "reward_gold": 15, "min_level": 1}


def combined_quest_feed() -> Iterator[Quest]:

   return itertools.chain(
        daily_quests(),
        guild_quests(),
        event_quests(),
    )


def endless_bounty_quests() -> Iterator[Quest]:
    for i in itertools.count(1):
        yield {
            "name": f"Bounty Posting #{i}",
            "reward_gold": 10 + i * 5,
            "min_level": 1 + i // 3,
        }


def first_n_bounties(n: int) -> List[Quest]:
    return list(itertools.islice(endless_bounty_quests(), n))


def quests_under_budget(quests: Iterable[Quest], budget: int) -> List[Quest]:
    sorted_quests = sorted(
        quests,
        key=lambda quest: quest["reward_gold"],
    )

    return list(
        itertools.takewhile(
            lambda quest: quest["reward_gold"] < budget,
            sorted_quests,
        )
    )


def group_roster_by_role(characters: Iterable[Character]) -> Dict[str, List[Character]]:
    sorted_characters = sorted(
        characters,
        key=lambda character: character.describe_role(),
    )

    return {
        role: list(group)
        for role, group in itertools.groupby(
            sorted_characters,
            key=lambda character: character.describe_role(),
        )
    }


def eligible_assignments(
    characters: Iterable[Character], quests: Iterable[Quest]
) -> List[tuple]:
    return [
        (character, quest)
        for character, quest in itertools.product(characters, quests)
        if character.level >= quest["min_level"]
    ]
