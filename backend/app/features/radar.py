def safe(v):
    try:
        v = float(v)
        return v if v == v else 0
    except:
        return 0


def clamp(x):
    return max(0, min(1, x))


def compute_player_radar(player: dict):
    scoring = (
        0.75 * safe(player.get("pctile_off_adj_rtg")) +
        0.25 * safe(player.get("pctile_off_usage"))
    )

    playmaking = (
        0.6 * safe(player.get("pctile_off_assist")) +
        0.25 * safe(player.get("pctile_off_ast_rim")) +
        0.15 * (1 - safe(player.get("pctile_off_to")))
    )

    defense = (
        0.4 * safe(player.get("pctile_def_adj_rapm")) +
        0.3 * safe(player.get("pctile_def_stl")) +
        0.3 * safe(1 - player.get("pctile_def_blk"))
    )

    rebounding = (
        0.6 * (1 - safe(player.get("pctile_def_reb"))) +
        0.4 * safe(player.get("pctile_off_reb"))
    )

    return [
        {"stat": "SCORING", "value": clamp(scoring)},
        {"stat": "PLAYMAKING", "value": clamp(playmaking)},
        {"stat": "DEFENSE", "value": clamp(defense)},
        {"stat": "REBOUNDING", "value": clamp(rebounding)},
    ]