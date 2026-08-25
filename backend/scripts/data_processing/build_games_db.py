"""Build a SQLite database of player game logs from the yearly JSON files.

Replaces loading an entire year's JSON (up to ~600MB in memory once parsed)
just to answer a single-player game-log request. The resulting DB is queried
by ncaa_id, so a request only pulls back the rows it needs.

Run after any update to backend/data/games/*.json(.gz):
    python scripts/data_processing/build_games_db.py

This is also run automatically during the Railway build (see railway.toml)
so the .db file itself does not need to be committed to git.
"""

import gzip
import json
import os
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
GAMES_DIR = DATA_DIR / "games"
DB_PATH = GAMES_DIR / "games.db"

YEARS = range(2019, 2027)

# Column order matches the fields present in the source JSON records.
# Kept as an explicit schema (rather than a JSON blob per row) so a
# player's game log can be read back as a few small, typed rows instead
# of re-parsing JSON text for every request.
COLUMNS = [
    ("ncaa_id", "TEXT"),
    ("year", "INTEGER"),
    ("numdate", "TEXT"),
    ("datetext", "TEXT"),
    ("opstyle", "INTEGER"),
    ("quality", "INTEGER"),
    ("win1", "INTEGER"),
    ("opponent", "TEXT"),
    ("muid", "TEXT"),
    ("win2", "INTEGER"),
    ("Min_per", "REAL"),
    ("ORtg", "REAL"),
    ("Usage", "REAL"),
    ("eFG", "REAL"),
    ("TS_per", "REAL"),
    ("ORB_per", "REAL"),
    ("DRB_per", "REAL"),
    ("AST_per", "REAL"),
    ("TO_per", "REAL"),
    ("dunksmade", "INTEGER"),
    ("dunksatt", "INTEGER"),
    ("rimmade", "INTEGER"),
    ("rimatt", "INTEGER"),
    ("midmade", "INTEGER"),
    ("midatt", "INTEGER"),
    ("twoPM", "REAL"),
    ("twoPA", "REAL"),
    ("TPM", "REAL"),
    ("TPA", "REAL"),
    ("FTM", "REAL"),
    ("FTA", "REAL"),
    ("bpm_rd", "REAL"),
    ("Obpm", "REAL"),
    ("Dbpm", "REAL"),
    ("bpm_net", "REAL"),
    ("pts", "INTEGER"),
    ("ORB", "REAL"),
    ("DRB", "REAL"),
    ("AST", "REAL"),
    ("TOV", "REAL"),
    ("STL", "REAL"),
    ("BLK", "REAL"),
    ("stl_per", "REAL"),
    ("blk_per", "REAL"),
    ("PF", "REAL"),
    ("possessions", "REAL"),
    ("bpm", "REAL"),
    ("sbpm", "REAL"),
    ("loc", "TEXT"),
    ("tt", "TEXT"),
    ("pp", "TEXT"),
    ("inches", "INTEGER"),
    ("cls", "TEXT"),
    ("pid", "INTEGER"),
]

FIELD_NAMES = [name for name, _ in COLUMNS if name != "ncaa_id" or True]


def load_year_records(year: int):
    gz_path = GAMES_DIR / f"{year}_player_game_data.json.gz"
    json_path = GAMES_DIR / f"{year}_player_game_data.json"

    if gz_path.exists():
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            return json.load(f)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def build():
    GAMES_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    col_defs = ", ".join(f"{name} {sqltype}" for name, sqltype in COLUMNS)
    cur.execute(f"CREATE TABLE games ({col_defs})")

    placeholders = ", ".join("?" for _ in COLUMNS)
    insert_sql = f"INSERT INTO games ({', '.join(FIELD_NAMES)}) VALUES ({placeholders})"

    total_rows = 0
    for year in YEARS:
        records = load_year_records(year)
        if records is None:
            print(f"  {year}: no source file, skipping")
            continue

        rows = [tuple(rec.get(name) for name in FIELD_NAMES) for rec in records]
        cur.executemany(insert_sql, rows)
        conn.commit()
        total_rows += len(rows)
        print(f"  {year}: inserted {len(rows)} rows")

    print("Building indexes...")
    cur.execute("CREATE INDEX idx_games_ncaa_id ON games(ncaa_id)")
    cur.execute("CREATE INDEX idx_games_ncaa_id_year ON games(ncaa_id, year)")
    conn.commit()

    conn.execute("VACUUM")
    conn.close()

    db_size_mb = os.path.getsize(DB_PATH) / 1024 / 1024
    print(f"Done. {total_rows} total rows. {DB_PATH} ({db_size_mb:.1f} MB)")


if __name__ == "__main__":
    build()
