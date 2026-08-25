from typing import Union, List
from fastapi import APIRouter, Query
import pandas as pd
from app.core.player_resolver import get_player_snapshot, get_player_all_time_percentiles
from app.core.data_loader import all_time_df
from app.features.moves import get_player_moves
from app.core.year_utils import normalize_year
from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams

router = APIRouter()


@router.get("/players/{ncaa_id}/moves")
def player_moves(ncaa_id: str, year: Union[int, str, None] = None):
    year = normalize_year(year)
    player = get_player_snapshot(ncaa_id, year)

    if not player:
        return {"error": "Player not found"}

    all_time_percentiles = get_player_all_time_percentiles(ncaa_id, year)

    if all_time_percentiles:
        for key, value in all_time_percentiles.items():
            if key.startswith('pctile_'):
                player[key] = value

    return get_player_moves(player)


@router.get("/moves/rankings")
def move_rankings(
    move_type: str = Query(..., description="Move type (rim_attack, sniper, mid_range, transition, pnr_maestro, post_dominator)"),
    year: Union[str, None] = Query(default=None, description="Year filter"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    position: Union[str, None] = Query(default=None, description="Position filter"),
    conference: Union[str, None] = Query(default=None, description="Conference filter"),
    high_major: Union[bool, None] = Query(default=None, description="Filter for high major conferences only"),
    search: Union[str, None] = Query(default=None, description="Search query for player name or team"),
    sort_by: Union[str, None] = Query(default="grade_score", description="Sort by field"),
    sort_order: Union[str, None] = Query(default="desc", description="Sort order (asc/desc)"),
):
    """Get rankings of players by a specific move type."""
    try:
        move_mapping = {
            "rim_attack": "off_style_rim_attack_ppp",
            "sniper": "off_style_perimeter_sniper_ppp",
            "mid_range": "off_style_mid_range_ppp",
            "transition": "off_style_transition_ppp",
            "pnr_maestro": "off_style_pnr_passer_ppp",
            "post_dominator": "off_style_post_up_ppp",
        }

        if move_type not in move_mapping:
            return {"error": f"Invalid move type. Must be one of: {list(move_mapping.keys())}"}

        ppp_column = move_mapping[move_type]
        ppp_pctile_column = f"pctile_{ppp_column}"
        frequency_pctile_column = f"pctile_{ppp_column.replace('_ppp', '_pct')}"

        if sort_by == "move_efficiency":
            sort_column = ppp_column
        elif sort_by == "move_frequency_pctile":
            sort_column = frequency_pctile_column
        elif sort_by == "grade_score":
            sort_column = f"move_{move_type}_grade_score"
        else:
            sort_column = ppp_column

        use_all_time = year is None or year == ""

        if use_all_time:
            if all_time_df.empty:
                return {"error": "All-time data not available"}
            source_df = all_time_df.copy()
        else:
            params = PlayerQueryParams(
                limit=limit,
                offset=0,
                sort=sort_column,
                order=sort_order or "desc",
                year=year if year != "career" else None,
                dataTier="enriched",
                search=search,
            )
            result = PlayerService.get_players(params)
            source_df = pd.DataFrame([r.model_dump() if hasattr(r, 'model_dump') else r for r in result.results])

        if position:
            source_df = source_df[source_df.get('Position') == position]

        if conference:
            conference_mapping = {
                'ACC': 'Atlantic Coast Conference',
                'Big 12': 'Big 12 Conference',
                'Big East': 'Big East Conference',
                'Big Ten': 'Big Ten Conference',
                'SEC': 'Southeastern Conference',
                'Pac-12': 'Pac 12 Conference',
                'Big West': 'Big West Conference',
                'Mountain West': 'Mountain West Conference',
                'West Coast': 'West Coast Conference',
                'Atlantic 10': 'Atlantic 10 Conference',
                'American': 'American Athletic Conference',
                'Conference USA': 'Conference USA',
                'Mid-American': 'Mid-American Conference',
                'Missouri Valley': 'Missouri Valley Conference',
            }
            full_conference = conference_mapping.get(conference, conference)
            source_df = source_df[source_df.get('conf') == full_conference]

        if high_major:
            high_major_conferences = [
                'Atlantic Coast Conference',
                'Big 12 Conference',
                'Big East Conference',
                'Big Ten Conference',
                'Southeastern Conference',
                'Pac 12 Conference'
            ]
            source_df = source_df[source_df.get('conf').isin(high_major_conferences)]

        if use_all_time and search:
            search_lower = search.lower()
            source_df = source_df[
                source_df.get('player_name', '').str.lower().str.contains(search_lower, na=False) |
                source_df.get('team', '').str.lower().str.contains(search_lower, na=False)
            ]

        reverse = sort_order != "asc"
        if sort_column in source_df.columns:
            source_df = source_df.sort_values(by=sort_column, ascending=not reverse)
        else:
            source_df = source_df.sort_values(by=ppp_column, ascending=not reverse)

        source_df = source_df.reset_index(drop=True)
        source_df['rank'] = source_df.index + 1

        total_filtered = len(source_df)
        source_df = source_df.iloc[offset:offset + limit]

        players_with_moves = []
        for _, player in source_df.iterrows():
            player_dict = player.to_dict()
            player_dict['rank'] = int(player['rank'])
            player_dict = {k: (None if pd.isna(v) else v) for k, v in player_dict.items()}
            player_dict["move_type"] = move_type
            player_dict["move_efficiency"] = player_dict.get(ppp_column, 0) or 0
            player_dict["move_usage"] = player_dict.get(f"{ppp_column.replace('_ppp', '_usg')}", 0) or 0
            player_dict["move_frequency_pctile"] = player_dict.get(frequency_pctile_column, 0) or 0
            ppp_pctile = player_dict.get(ppp_pctile_column, 0) or 0
            player_dict["move_efficiency_pctile"] = ppp_pctile

            precalc_score_column = f"move_{move_type}_grade_score"
            precalc_grade_column = f"move_{move_type}_grade"
            player_dict["grade_score"] = player_dict.get(precalc_score_column, 0) or 0
            player_dict["grade"] = player_dict.get(precalc_grade_column, "F") or "F"

            if player_dict.get("year") is None or player_dict.get("year") == 0:
                player_dict["year"] = player.get("year", None)
            
            players_with_moves.append(player_dict)

        return {
            "results": players_with_moves,
            "count": len(all_time_df) if use_all_time else result.count,
            "filtered_count": total_filtered,
            "success": True
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}