import numpy as np

def safe(v):
    try:
        if v is None:
            return 0
        return float(v)
    except:
        return 0


def make_move(player, name, key, category, pctile_key):
    return {
        "name": name,
        "efficiency": safe(player.get(f"{key}_ppp")),
        "efficiencyPctile": safe(player.get(f"pctile_{key}_ppp")),
        "usage": safe(player.get(f"{key}_pct")),
        "frequencyPctile": safe(player.get(pctile_key)),
        "category": category,
    }


def get_player_moves(player):
    moves = [
        make_move(
            player,
            "Rim Attack",
            "off_style_rim_attack",
            "finishing",
            "pctile_off_style_rim_attack_pct",
        ),
        make_move(
            player,
            "Sniper",
            "off_style_perimeter_sniper",
            "shooting",
            "pctile_off_style_perimeter_sniper_pct",
        ),
        make_move(
            player,
            "Mid-Range Assassin",
            "off_style_mid_range",
            "shooting",
            "pctile_off_style_mid_range_pct",
        ),
        make_move(
            player,
            "Transition Bolt",
            "off_style_transition",
            "finishing",
            "pctile_off_style_transition_pct",
        ),
        make_move(
            player,
            "PnR Maestro",
            "off_style_pnr_passer",
            "playmaking",
            "pctile_off_style_pnr_passer_pct",
        ),
        make_move(
            player,
            "Post Dominator",
            "off_style_post_up",
            "interior",
            "pctile_off_style_post_up_pct",
        ),
    ]

    moves = [m for m in moves if m["usage"] > 0.01]

    moves.sort(key=lambda m: m["efficiency"] * m["usage"], reverse=True)

    return moves[:6]