CREATE TYPE CHARACTER_TYPE AS ENUM ('warrior', 'mage', 'rogue');
CREATE TYPE ABILITY_TYPE AS ENUM ('tank', 'healer');
CREATE TYPE RARITY_TYPE AS ENUM ('common', 'uncommon', 'rare', 'epic', 'legendary');

CREATE TABLE roster (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE character (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    hp INTEGER NOT NULL CHECK (hp >= 0),
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 100),
    type CHARACTER_TYPE NOT NULL,
    roster_id INTEGER REFERENCES roster(id) ON DELETE SET NULL
    -- SET NULL because character can exist outside of roaster
);
CREATE INDEX idx_character_roster_id ON character(roster_id);

CREATE TABLE ability (
    id SERIAL PRIMARY KEY,
    ability_type ABILITY_TYPE UNIQUE NOT NULL,
    -- ability_type itself could be the PRIMARY KEY but assignement says every entity should have a SERIAL id
    taunt_radius INTEGER CHECK (taunt_radius >= 0),
    -- taunt radius only relevent for tank
    heal_power INTEGER CHECK (heal_power >= 0),
    -- heal_power only relevent for healer
    CHECK (
        (ability_type = 'tank' AND taunt_radius IS NOT NULL AND heal_power IS NULL) OR
        (ability_type = 'healer' AND heal_power IS NOT NULL AND taunt_radius IS NULL)
    )
);

CREATE TABLE character_ability (
    character_id INTEGER REFERENCES character(id) ON DELETE CASCADE,
    -- if character is deleted. no ability should be linked to it
    ability_id INTEGER REFERENCES ability(id) ON DELETE CASCADE,
    -- if ability is deleted. no character has it
    PRIMARY KEY (character_id, ability_id)
);
CREATE INDEX idx_character_ability_ability_id ON character_ability(ability_id);

CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    value INTEGER NOT NULL CHECK (value >= 0),
    rarity RARITY_TYPE NOT NULL
);

CREATE TABLE character_item (
    character_id INTEGER REFERENCES character(id) ON DELETE CASCADE,
    -- if character is deleted, it loses his items
    item_id INTEGER REFERENCES item(id) ON DELETE CASCADE,
    -- if item is deleted, no character should own it
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (character_id, item_id)
);
CREATE INDEX idx_character_item_item_id ON character_item(item_id);

CREATE TABLE quest (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    reward_gold INTEGER NOT NULL CHECK (reward_gold >= 0),
    min_level INTEGER NOT NULL CHECK (min_level >= 1)
);

CREATE TABLE character_quest (
    character_id INTEGER REFERENCES character(id) ON DELETE CASCADE,
    quest_id INTEGER REFERENCES quest(id) ON DELETE CASCADE,
    PRIMARY KEY (character_id, quest_id)
);
CREATE INDEX idx_character_quest_quest_id ON character_quest(quest_id);
