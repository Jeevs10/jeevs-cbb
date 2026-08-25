from typing import Dict, Any, List

def safe(v):
    try:
        if v is None:
            return 0
        return float(v)
    except:
        return 0


def get_level(pct: float) -> int:
    if pct > 0.97:
        return 5
    if pct > 0.95:
        return 4
    if pct > 0.90:
        return 3
    if pct > 0.85:
        return 2
    if pct > 0.80:
        return 1
    return 0

def normalize_minutes(mins):
    m = safe(mins)
    if m <= 0:
        return 0
    return min(1.0, m / 38.0)


def sniper_score(player):
    made = safe(player.get("ThreePointFieldGoals Made"))
    att = safe(player.get("ThreePointFieldGoals Attempted"))
    pct = safe(player.get("ThreePointFieldGoals Pct"))

    if att < 100:
        return 0

    if pct < 0.33:
        return 0

    volume = min(1.0, att / 250.0)

    if att >= 200:
        req = 0.35
    elif att >= 150:
        req = 0.40
    elif att >= 100:
        req = 0.45
    else:
        req = 1.0

    if pct < req:
        return 0

    efficiency_score = (pct - req) / (0.55 - req)
    efficiency_score = max(0.0, min(1.0, efficiency_score))

    return min(1.0, 0.6 * volume + 0.4 * efficiency_score)


def microwave_score(player):
    pts = safe(player.get("Points"))
    usage = safe(player.get("Usage"))
    ts = safe(player.get("TrueShootingPct"))

    if usage < 0.20:
        return 0

    return min(
        min(1.0, pts / 22.0),
        ts
    )


def ironman_score(player):
    mins = safe(player.get("Minutes"))
    games = safe(player.get("Games"))
    starts = safe(player.get("Starts"))

    if games < 20:
        return 0

    if mins <= 0:
        return 0

    total_team_minutes = games * 40
    if total_team_minutes == 0:
        return 0

    minute_share = mins / total_team_minutes

    start_rate = starts / games if games > 0 else 0

    raw = 0.75 * minute_share + 0.3 * start_rate

    return min(1.0, raw)

def make_badge(name: str, level: int, category: str):
    return {
        "name": name,
        "level": level,
        "category": category
    }


def usage_filtered_score(usage, ppp):
    usage_val = safe(usage)
    ppp_val = safe(ppp)

    if usage_val < 0.30:
        return 0

    return min(usage_val, ppp_val)


def get_player_badges(player: Dict[str, Any]) -> List[Dict]:
    if not player:
        return []

    badges = []

    def add(name, score, category):
        lvl = get_level(score)
        if lvl > 0:
            badges.append(make_badge(name, lvl, category))

    add("Deadeye", usage_filtered_score(
        player.get("pctile_off_style_perimeter_sniper_usg"),
        player.get("pctile_off_style_perimeter_sniper_ppp")
    ), "scoring")

    add("True Sniper", sniper_score(player), "scoring")
    add("Microwave Scorer", microwave_score(player), "scoring")

    add("Movement Shooter", usage_filtered_score(
        player.get("pctile_off_style_perimeter_sniper_usg"),
        player.get("pctile_off_style_perimeter_sniper_ppp")
    ), "scoring")

    add("Shot Architect", usage_filtered_score(
        player.get("pctile_off_style_dribble_jumper_usg"),
        player.get("pctile_off_style_dribble_jumper_ppp")
    ), "scoring")

    add("Midrange Magician", usage_filtered_score(
        player.get("pctile_off_style_mid_range_usg"),
        player.get("pctile_off_style_mid_range_ppp")
    ), "scoring")

    add("Rim Attacker", usage_filtered_score(
        player.get("pctile_off_style_rim_attack_usg"),
        player.get("pctile_off_style_rim_attack_ppp")
    ), "scoring")

    add("Lob Threat", usage_filtered_score(
        player.get("pctile_off_style_big_cut_roll_usg"),
        player.get("pctile_off_style_big_cut_roll_ppp")
    ), "big")

    add("Paint Punisher", usage_filtered_score(
        player.get("pctile_off_style_post_up_usg"),
        player.get("pctile_off_style_post_up_ppp")
    ), "big")

    add("Pick & Pop", usage_filtered_score(
        player.get("pctile_off_style_pick_pop_usg"),
        player.get("pctile_off_style_pick_pop_ppp")
    ), "big")

    add("PnR Maestro", usage_filtered_score(
        player.get("pctile_off_style_pnr_passer_usg"),
        player.get("pctile_off_style_pnr_passer_ppp")
    ), "playmaking")

    add("Drive & Dish Dynamo", usage_filtered_score(
        player.get("pctile_off_style_attack_kick_usg"),
        player.get("pctile_off_style_attack_kick_ppp")
    ), "playmaking")

    add("Floor General", min(
        safe(player.get("pctile_off_assist")),
        1 - safe(player.get("pctile_off_to"))
    ), "playmaking")

    add("Tempo Controller", safe(player.get("pctile_off_assist")), "playmaking")

    add("Backdoor Bandit", usage_filtered_score(
        player.get("pctile_off_style_hits_cutter_usg"),
        player.get("pctile_off_style_hits_cutter_ppp")
    ), "iq")

    add("Off-Ball Savant", usage_filtered_score(
        player.get("pctile_off_style_perimeter_cut_usg"),
        player.get("pctile_off_style_perimeter_cut_ppp")
    ), "iq")

    add("Rim Protector", safe(player.get("pctile_def_blk")), "defense")

    add("Pickpocket", 
        safe(player.get("pctile_def_stl")),"defense")
    
    pg_conf = safe(player.get("posConfidences[_PG_]"))
    
    c_conf = safe(player.get("posConfidences[_C_]"))
    
    add("Perimeter Lock", min(
    safe(player.get("pctile_def_stl")),
    1 - c_conf
), "defense")

    add("Glass Cleaner", safe(1 - player.get("pctile_def_reb")), "hustle")
    add("Second Chance King", safe(player.get("pctile_off_orb")), "hustle")

    add("Fastbreak Phenom", usage_filtered_score(
        player.get("pctile_off_style_transition_usg"),
        player.get("pctile_off_style_transition_ppp")
    ), "scoring")

    add("Offensive Engine", safe(player.get("pctile_off_usage")), "role")

    add("Elite Finisher", min(
        safe(player.get("pctile_off_team_poss_pct")),
        1 - safe(player.get("pctile_off_assist"))
    ), "role")

    add("Primary Creator", min(
        pg_conf,
        safe(player.get("pctile_off_assist"))
    ), "role")

    add("Interior Anchor", min(
        c_conf,
        safe(player.get("pctile_def_blk"))
    ), "defense")
    add("Unicorn", min(
    safe(player.get("pctile_off_style_pick_pop_ppp")),
    safe(player.get("pctile_def_blk"))
), "rare")

    # two-way star
    add("Two-Way Star", min(
        safe(player.get("pctile_def_blk")),
        safe(player.get("pctile_off_usage"))
    ), "rare")

    add("Chaos Agent", min(
        safe(player.get("pctile_def_stl")),
        safe(player.get("pctile_off_style_transition_ppp"))
    ), "rare")

    add("Iron Man", ironman_score(player), "role")

    return sorted(badges, key=lambda x: x["level"], reverse=True)[:12]