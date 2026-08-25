"""Shared raw roster-info CSV loader.

backend/data/players/{year}-roster-info.csv was previously parsed
independently by data_loader.py, team_data_loader.py, and player_graph.py -
three separate pandas parses of the same ~16MB of CSVs at process startup
(plus a fourth re-parse on every player_graph reload_with_filters() call).
This module parses each year's CSV once and caches the raw, minimally-typed
per-year frames; callers derive their own filtered/typed view on top instead
of hitting disk again.
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent.parent.parent
PLAYERS_DIR = BASE_DIR / "data" / "players"

_raw_roster_frames = None


def _load_raw_roster_frames():
    """Read each year's roster-info.csv once. Returns {year: DataFrame}."""
    global _raw_roster_frames
    if _raw_roster_frames is not None:
        return _raw_roster_frames

    frames = {}
    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}-roster-info.csv"
        if csv_path.exists():
            df_year = pd.read_csv(csv_path)
            df_year["Season"] = df_year["Season"].astype(str)
            df_year["year"] = pd.to_numeric(df_year["Season"], errors="coerce")
            frames[year] = df_year

    _raw_roster_frames = frames
    return frames


def get_roster_data(years=None):
    """Combined roster-info rows for the given years (default: all available).

    Returns raw, unfiltered rows - callers apply their own conference
    filtering and id-column dtype handling on top of this.
    """
    frames = _load_raw_roster_frames()
    years_to_load = years if years else sorted(frames.keys())

    selected = [frames[y] for y in years_to_load if y in frames]
    if not selected:
        return pd.DataFrame()

    return pd.concat(selected, ignore_index=True)
