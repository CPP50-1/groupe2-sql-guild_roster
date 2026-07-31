# Guild Roster DataBase - prep for HTML/CSS

You should have a decision log with your group's reconciled domain model,
this is where you turn it into a real database, then into the data and queries
the HTML/CSS block will actually build against.

---

## Part 1 - Schema & DDL

### 1. Decision log -> Column plan

The 1-N/N-N decisions have been made during the merge_and_decide.
Now, to turn it into a column-level plan :

- [x] Every attribute → pick one type (`INTEGER`, `VARCHAR(n)`, `NUMERIC`,
      `DATE`, `BOOLEAN`...).
- [x] Every categorical attribute (status, rarity, class...) → write out its
      fixed list. This becomes a `CHECK` later.
- [x] Every entity → gets a `SERIAL` `id`. Any natural identifier (a unique
      name, a code) → add `UNIQUE` on top, don't replace the surrogate with it.
- [x] Ambiguous 1-N/N-N call from merge-and-decide → resolve now, not later.

> Write this as an extension of your decision log (e.g.
> match(
> id: SERIAL PK,
> tournament_id: INTEGER FK -> tournament.id, ON DELETE CASCADE,
> round_number: INTEGER CHECK (>= 1),
> status: VARCHAR(10) CHECK IN ('scheduled','live','finished')
> ))

### 2. write the DDL

> DDL -> Data Definition Language : structure of the database (CREATE TABLE) <br/>
> DML -> Data Manipulation Language : manipulate the rows (SELECT / INSERT / UPDATE / DELETE) <br/>
> DCL -> Data Control Language : permissions (GRANT / REVOKE)

Produce a complete `CREATE TABLE` set:

- [ ] One `CREATE TABLE` per entity.
- [ ] One junction table per N-N relation. Relationship-owned attribute → </br>
      column on the junction table, not on either side.
- [ ] FKs with a deliberate `ON DELETE` choice on each, be ready to say out loud
      why you picked `CASCADE` vs `SET NULL` vs `RESTRICT` for each one.
- [ ] An index on every FK column (Postgres does not create these automatically).

**Cross-group review:** once your group's DDL is written, present it to
another group and justify your modeling choices.

**Deliverable:** `schema.sql`, ready to apply.

**Example output** schema & DDL

> Starting from this short imaginary decision log
>
> - Tournament -> 1-N root, holds many Match rows.
> - Match -> belongs to exactly one Tournament; has a status (scheduled / live / finished) : a categorical attribute, fixed list.
> - Achievement -> has a tier (bronze / silver / gold), another fixed list.
> - character ↔ Achievement -> N-N. A character can earn several achievements; the same achievement can be earned by several characters.
> - Relationship-owned attribute: earned_at, belongs to the character-achievement pairing, not to either side alone.

```
# note that constraint names follow a plain convention (tablename_columnname_check / _fkey)
# Postgres generates these automatically if you don't name them yourself, and it's what you'll see when you introspect your own schema later.

# `psql`'s \d tablename output examples your schema should produce :
Table "public.tournament"
   Column   |          Type          | Collation | Nullable |               Default
------------+------------------------+-----------+----------+-----------------------------------------
 id         | integer                |           | not null | nextval('tournament_id_seq'::regclass)
 name       | character varying(100) |           | not null |
 season     | character varying(20)  |           | not null |
 prize_pool | integer                |           | not null |
Indexes:
    "tournament_pkey" PRIMARY KEY, btree (id)
    "tournament_name_key" UNIQUE CONSTRAINT, btree (name)
Check constraints:
    "tournament_prize_pool_check" CHECK (prize_pool >= 0)
Referenced by:
    TABLE "match" CONSTRAINT "match_tournament_id_fkey"
        FOREIGN KEY (tournament_id) REFERENCES tournament(id) ON DELETE CASCADE
---
Table "public.match"
    Column     |          Type          | Collation | Nullable |             Default
---------------+------------------------+-----------+----------+-----------------------------------
 id            | integer                |           | not null | nextval('match_id_seq'::regclass)
 tournament_id | integer                |           | not null |
 round_number  | integer                |           | not null |
 status        | character varying(10)  |           | not null | 'scheduled'::character varying
Indexes:
    "match_pkey" PRIMARY KEY, btree (id)
    "idx_match_tournament_id" btree (tournament_id)
Check constraints:
    "match_round_number_check" CHECK (round_number >= 1)
    "match_status_check" CHECK (status::text = ANY (ARRAY['scheduled', 'live', 'finished']))
Foreign-key constraints:
    "match_tournament_id_fkey" FOREIGN KEY (tournament_id)
        REFERENCES tournament(id) ON DELETE CASCADE
```

---

## Part 2 - Seed, queries, export

### 1. Seeding - Populate the database

- [ ] Write the insert script. `%s` placeholders only, never an f-string
      or `+` into a query.

> Script that iterates your real domain objects using the container/iterator protocol you built during the OOP part.

- [ ] Add synthetic volume (generate_series, or a small random-data script) - enough rows for pagination/filtering to be non-trivial later.
- [ ] Wrap the whole seed in one transaction.
- [ ] Test 1: break a `CHECK` on purpose mid-seed → confirm the whole batch
      rolls back, including the earlier valid inserts.
- [ ] Test 2: same insert, concatenated vs parameterized → try to smuggle
      a `'; DROP TABLE ...` value through the concatenated one.
- [ ] Every insert another insert depends on → capture the new `id` with
      `RETURNING`, use it in the next insert.

**Example** seeding

```python
#--- Wrapped in BEGIN/COMMIT, the whole seed is one unit of work.
with conn:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tournament (name, season, prize_pool) VALUES (%s, %s, %s) RETURNING id",
            ("Ashfall Open", "2026", 5000),
        )
        tournament_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO match (tournament_id, round_number, status) VALUES (%s, %s, %s)",
            (tournament_id, 1, "finished"),
        )
#--- Rollback checkpoint : Deliberately violate one of your own CHECK constraints partway through a multi-insert transaction.
# What you should see come back is something like:
#       psycopg2.errors.CheckViolation: new row for relation "match"
#       violates check constraint "match_round_number_check"
#       DETAIL:  Failing row contains (4, 1, 0, scheduled).
```

### 2. The queries that feed HTML/CSS, then export

Write these four series of queries, each one becomes the input to a
specific part of the HTML/CSS block that follows:

- [ ] 1 - Full roster, `JOIN` across your 1-N relation
- [ ] 2 - KPI-style aggregates (active count, in-progress count, low-HP / low-stock alerts) - **One query per KPI**
- [ ] 3 - A list for the status and one for the rarity - entity + category together
- [ ] 4 - Schema introspection - **3 queries**
    - columns, types, constraints, allowed values, via `information_schema`
    - constraints overview (`table_constraints` + `constraint_column_usage`)
    - actual `CHECK` values (`pg_constraint`)
      Keep the introspection queries at "give me a table's columns, types, and
      constraints".

| Queries        | Web basics part it will Feed                                     |
| -------------- | ---------------------------------------------------------------- |
| 1 JOIN         | 1 - semantic refactor of the roster table (+ Flexbox/Grid)       |
| 2 KPI          | 2 - dashboard: layout **and** SCSS theme, built together         |
| 3 List         | 2 - drives the SCSS state-based styling (rarity/status → visual) |
| 4 Schema intro | 3 - Bootstrap form where every field mirrors a real constraint   |

**Deliverable:** export each of the four query results to CSV or JSON
(`\copy ... TO`, or a query + Python serialization), these files are what
you hand to the HTML/CSS block.

**Example of output** for the 4 types of queries

1. `JOIN` across your 1-N relation

```
 id | round_number | status    | tournament_name
----+--------------+-----------+-----------------
  1 |            1 | finished  | Ashfall Open
  2 |            2 | live      | Ashfall Open
  3 |            1 | scheduled | Ember Cup
```

2. KPI-style aggregates

> You can find some example queries here : https://datatas.com/how-to-build-kpi-dashboards-with-sql/

```
# ! Ember Cup still appears at 0
tournament_name | live_matches
----------------+--------------
Ashfall Open    | 2
Ember Cup       | 0

# Characters with zero achievements
name
------
Thane
Finn
```

3. List with status/tier column

```
# In this example we rank the 'live' status first on purpose ('live' status "deserves more attention", it appends now).
# Each row shows which entity has which value.
round_number | tournament_id | status
-------------+---------------+-----------
2            | 1             | live
1            | 2             | scheduled
1            | 1             | finished

# `tier` is a plain VARCHAR, if your result comes back alphabetical (bronze, gold, silver) instead of ranked like this, the column's natural sort order is what you're fighting; hint : You can use `CASE` in `ORDER BY` to choose the order yourself.
title        | tier
-------------+--------
Undefeated   | gold
Iron Will    | silver
First Blood  | bronze
```

4. Schema introspection

```
-- Columns, types, nullability for one table
 column_name    | data_type         | is_nullable | column_default
----------------+-------------------+-------------+--------------------------------
 id             | integer           | NO          | nextval('match_id_seq'::regclass)
 tournament_id  | integer           | NO          | NULL
 round_number   | integer           | NO          | NULL
 status         | character varying | NO          | 'scheduled'::character varying

conname            | definition
-------------------+-----------------------------------------------------------
match_status_check | CHECK ((status)::text = ANY (ARRAY['scheduled', 'live', 'finished']))

-- Constraints (PK, FK, CHECK, UNIQUE) on a given table
constraint_name            | constraint_type | column_name
---------------------------+-----------------+-------------
match_pkey                 | PRIMARY KEY     | id
match_tournament_id_fkey   | FOREIGN KEY     | id
match_round_number_check   | CHECK           | round_number
match_status_check         | CHECK           | status

-- The actual allowed values behind a CHECK constraint. information_schema
-- alone will tell you a CHECK exists, but not what it checks, that text
-- only lives in Postgres's own catalog, not the ANSI-standard views.
conname            | definition
-------------------+-----------------------------------------------------------
match_status_check | CHECK ((status)::text = ANY (ARRAY['scheduled', 'live', 'finished']))

```

---

## Check list before the web basics part.

By the end of the SQL part, your group should have:

- [ ] `schema.sql`
- [ ] A seeded database
- [ ] The four exports (roster, KPIs, status/rarity list, schema introspection)
- [ ] Decision log, updated with any schema-level calls made later in the process

> That's the complete input to the HTML/CSS block, and it's also, not
> coincidentally, most of what a light ORM needs to know about your schema:
>
> - The DDL it maps
> - The parameterized-write pattern its query builder will use
> - The introspection query that lets it discover a schema instead of having
>   everything hardcoded.
