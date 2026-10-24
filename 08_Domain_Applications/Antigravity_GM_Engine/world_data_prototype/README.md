# NBA2K22 World Data — initial executable SQLite prototype

**Development mainline / synthetic-fixture phase — not Native acceptance or production migration.**

The Human-approved design uses **one SQLite database per independent NBA2K22 game save** and typed attribute/tendency snapshots plus separate badge/PlayType children.

This first engineering increment implements **16 SQLite tables** out of the **59-table provisional architecture catalog**. All real game data, existing save files, game processes, legacy `database/schema.sql`, and production migration remain untouched.

## Run

From repository root:

```bash
python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p 'test_*.py' -v
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py smoke
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py init <new-file.sqlite> <independent-save-id>
```

The `smoke` command creates a disposable **synthetic** database. `init` refuses to overwrite an existing file, and `demo` populates a new file with explicitly synthetic data.

## Verified in isolated development runtime

- 11 Python `unittest` cases passed; the smoke run reported 16 tables, 2 game Box observations, 2 typed attribute observations, 2 capture units and zero SQLite foreign-key errors.
- Per-save ID is immutable; mismatched source save ID is refused; unrelated saves have no parent/fork/merge relationship.
- Successful capture consistency units are append-only. Same exact unit replay is idempotent; two separate units with unchanged values remain two real observation records; failed units cannot populate facts.
- Game, team, player, season and Box are tied by actual SQLite foreign keys.
- Badge and PlayType are separate typed relational child records.
- No hidden player Potential is accepted into public attribute snapshots or included in GM query views.
- **These tests used synthetic fixtures, not a running game.** Existing Native research labels remain unverified by this task.

## Next engineering increments

Connect separately proven, **read-only** PC NBA2K22 Reader/Decoder adapters when the dedicated test machine is connected. Iterate the 59-table candidate design based on actual game source fields, implement the remaining coach/team/draft/finance/settings/honors areas and their column dictionaries and source evidence, then complete whole-system validation and independent review.

OS task packet and verification plan: `01_os/07_content/_runs/run-20261024-nba2k22-world-data-prototype-001/`.
