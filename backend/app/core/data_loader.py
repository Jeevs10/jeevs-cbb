import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_players():

    csv_2025 = os.path.join(BASE_DIR, "data", "2025-players_enriched.csv")
    csv_2026 = os.path.join(BASE_DIR, "data", "2026-players_enriched.csv")

    df_2025 = pd.read_csv(csv_2025)
    df_2026 = pd.read_csv(csv_2026)

    # -------------------------
    # FORCE CLEAN YEAR FORMAT
    # -------------------------

    df_2025["year"] = 2025
    df_2026["year"] = 2026

    df = pd.concat([df_2025, df_2026], ignore_index=True)

    # force numeric safety
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)

    return df


df = load_players()

players_df = (
    df.sort_values(["player_code", "year"])
      .groupby("player_code")
      .tail(1)
)

PLAYER_LOOKUP = players_df.set_index("player_code").to_dict("index")