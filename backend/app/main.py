from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("players.csv")

# Only allow safe sortable columns (IMPORTANT)
ALLOWED_SORTS = {
    "off_rtg",
    "def_rtg",
    "adj_rapm_margin",
    "adj_prod_margin",
    "off_adj_rtg",
    "def_adj_rtg",
    "off_usage",
    "off_assist",
    "off_efg",
}

@app.get("/players")
def get_players(
    limit: int = 50,
    offset: int = 0,
    sort: str = "adj_rapm_margin",
    order: str = "desc",
    year: int | None = None,
    conf: str | None = None
):
    data = df.copy()

    if year:
        data = data[data["year"] == year]

    if conf:
        data = data[data["conf"] == conf]

    if sort not in ALLOWED_SORTS:
        sort = "adj_rapm_margin"

    data = data.sort_values(by=sort, ascending=(order == "asc"))

    data = data.iloc[offset:offset + limit]

    # 🔥 CRITICAL FIX
    data = data.replace({np.nan: None})

    return {
        "count": len(df),
        "results": data.to_dict(orient="records")
    }


@app.get("/players/{player_code}")
def get_player(player_code: str):
    player = df[df["player_code"] == player_code]
    
    if player.empty:
        return {"error": "Player not found"}

    record = player.iloc[0].to_dict()

    record = {
        k: (None if pd.isna(v) else v)
        for k, v in record.items()
    }

    record = nest_player(player.iloc[0].to_dict())
    return record

def nest_player(row):
    out = {}

    for k, v in row.items():
        if "." in k:
            parent, child = k.split(".", 1)
            if parent not in out:
                out[parent] = {}
            out[parent][child] = None if pd.isna(v) else v
        else:
            out[k] = None if pd.isna(v) else v

    return out