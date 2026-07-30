
# Merge & Decide

There is a debate on what a Guild is. Since the concept doesn't clearly emerge from the code base. It is left off: It is considered a Guild is equivalent to a Roster.

The following entities (along with attributes and examples) and relationships between them have been finally identified and agreed upon:

**Entities & key attributes**

- `Character` - name, hp, level, *base_hp*, abilities (ex: Mage)
- `Ability`- name
  - 'Tank' - taunt_radius
  - 'Healer' - heal_power
- `Item` - name, value, rarity (`COMMON`/`UNCOMMON`/`RARE`/`EPIC`/`LEGENDARY`)
- `Roster` - characters
- `Quest` - name, reward, min_level
  - `Daily`
  - `Guild`
  - `Event`
- `Dungeon` - floors
- `Floor` - floor_number
  - `monster` - name, hp, attack
  - `trap` - damage
  - `loot_chest` - loot         (could be gold or item? gold is kinda like an item)

**Relations**

| Relation                 | Type (note)          | Rationale behind it                                                                                                            |
|--------------------------|----------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `Roster` <-> `Character` | 0..1 - 1..N          | a Character can be in none or at most one Roster; a Roster has no existence without characters and can contain several of them |
| `Quest` <-> `Character`  | 0..N - 0..N (note 1) | a Quest can be assigned to no or several Characters; a Character could do many Quest at the same time                          |
| `Character` -> `Item`    | 0..N - 0..N (note 2) | a Character could have none or many Items. An item is owned by                                                                 |
| `Dungeon` -> `Floor`     | 1-N                  | a Dungeon is made of one to many Floor                                                                                         |


Notes:
(1) There is discussion about 
- whether the Quest is assigned to a Roster or a Character. The quest_assignment function suggests it is assigned to one (or some) Character(s) and relates to the Roster through him (or them). 

(2) There is a discussion on what the Item represents. 
- If it represents a generic item (eg. a sword):
  - the relationship towards Character is 0..N : More than one Character can have such an item.
  - the relationship of Character towards Item is 0..1 if the Character can have a maximum of such an item. It is 0..N if a Character can have more than one such item.

- If it represents a specific item with a proper identity (eg. The Excalibur sword)
  - the relationship towards Character is 0..<b>1</b> : Only one Character may possess that specific item
  - the relationship of Character towards Item is 0..<b>N</n> : A Character may possess zero or more specific items

The following domain processes are also identified:
- battle — involves a Character vs. one implicit enemy
- floor_encounter — involves a Character encountering some obstacles (trap, monster, loot_chest)
