from fastapi import APIRouter
from app.services.similarity_service import get_similar_players
from app.core.data_loader import PLAYER_LOOKUP
from app.core.year_utils import normalize_year

router = APIRouter()


def enrich(results):
    def format_list(lst):
        out = []

        for item in lst:
            code = item["player_code"]
            meta = PLAYER_LOOKUP.get(code, {})

            out.append({
                "player_code": code,
                "player_name": meta.get("player_name"),
                "team": meta.get("team"),
                "pos": meta.get("posClass"),

                # IMPORTANT: snapshot year used in comparison
                "year": item.get("year"),

                "similarity": item.get("similarity", 0),
                "reasons": item.get("reasons", []),
            })

        return out

    return {
        "style": format_list(results["style"]),
        "impact": format_list(results["impact"]),
        "combined": format_list(results["combined"]),
    }


@router.get("/players/{player_code}/similar")
def similar_players(
    player_code: str,
    year: int | str | None = None,
    top_k: int = 10,
    style_weight: float = 0.7
):

    year = normalize_year(year)

    results = get_similar_players(
        player_code,
        year=year,
        top_k=top_k,
        style_weight=style_weight
    )

    return enrich(results)