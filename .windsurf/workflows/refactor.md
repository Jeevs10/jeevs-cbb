# Windsurf Refactor Workflow

## Objective

Refactor the repository to improve structure, consistency, performance, and scalability.

---

## Phase 1: Repository Audit (Read-Only)

### Goals

* Understand full project structure
* Map frontend ↔ backend interactions
* Identify duplicate logic and inconsistencies

### Tasks

* Document folder structure
* Trace API calls from frontend to backend
* Identify duplicate functions
* Identify mixed responsibilities

### Output

* High-level architecture map

---

## Phase 2: Define Data Contract (Critical)

### Primary Keys

* `player_id = roster.ncaa_id`
* `year`

### Schema Definition

* Standardize all column names and types
* Ensure consistent usage across backend

### Rules

* No function should rely on `player_code`
* All joins must use `(player_id, year)`

---

## Phase 3: Data Layer Refactor

### Create Structure

```
backend/app/data/
  loader.py
  cleaner.py
  merger.py
  schema.py
```

### Responsibilities

* loader: read raw data
* cleaner: normalize IDs and years
* merger: join datasets
* schema: enforce consistency

---

## Phase 4: Player Identity Migration

### Steps

1. Introduce `player_id` as alias for `roster.ncaa_id`
2. Update backend functions to use `player_id`
3. Update frontend API routes to use `player_id`
4. Keep `player_code` temporarily for compatibility

---

## Phase 5: API Refactor

### Structure

```
routes/
  players.py
  search.py
  stats.py
```

### Separation of Concerns

* `/players` → list + filtering
* `/players/{id}` → single player
* `/search` → search logic only

---

## Phase 6: Remove Duplication

### Targets

* normalize_year
* ID cleaning logic
* repeated pandas filters

### Extract To

```
core/utils/
  ids.py
  years.py
  filters.py
```

---

## Phase 7: Performance Optimization

### Improvements

* Preload cleaned dataset once (no repeated df.copy())
* Add indexing:

  * `(player_id, year)`
* Precompute search columns
* Cache API responses

---

## Phase 8: Frontend Cleanup

### Rules

* Frontend handles display only
* Backend handles all logic

### Structure

```
frontend/
  api/
  hooks/
  components/
```

---

## Phase 9: Data Integrity Checks

### Add Assertions

* No null player_id
* No duplicate `(player_id, year)` pairs
* Schema consistency enforced

---

## Phase 10: Future-Proofing

### Introduce Repository Layer

Example:

```
class PlayerRepository:
    def get_player(self, player_id, year):
        pass

    def search(self, query):
        pass
```

### Benefits

* Easier migration to database
* Centralized data access
* Cleaner API layer

---

## Final Goal Architecture

```
CSV → Data Layer → Repository → API → Frontend
```

---

## Execution Notes

* Complete phases sequentially
* Validate after each phase
* Do not mix refactor + feature development
* Keep changes small and testable

---

## Completion Criteria

* All endpoints use `player_id`
* No duplicate logic exists
* Data joins are stable and deterministic
* App performance improved
* Codebase is modular and exte
