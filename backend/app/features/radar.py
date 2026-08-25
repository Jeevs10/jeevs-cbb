def safe(v):
    try:
        v = float(v)
        return v if v == v else 0
    except:
        return 0


def clamp(x):
    return max(0, min(1, x))


def normalize_stat(value, min_val, max_val):
    """Normalize a stat value to 0-1 range"""
    if max_val == min_val:
        return 0.5
    return clamp((value - min_val) / (max_val - min_val))


def invert_normalize(value, min_val, max_val):
    """Normalize a stat where smaller is better (e.g., TO%)"""
    if max_val == min_val:
        return 0.5
    # Invert: smaller values get higher radar values
    return clamp(1 - (value - min_val) / (max_val - min_val))


def compute_player_radar(player: dict, preset: str = "overview", custom_fields: list = None):
    # Define stat ranges for normalization
    stat_ranges = {
        "PPG": (0, 30),
        "RPG": (0, 15),
        "APG": (0, 10),
        "SPG": (0, 3),
        "BPG": (0, 3),
        "MPG": (0, 40),
        "FG%": (0.3, 0.6),
        "3P%": (0.2, 0.45),
        "FT%": (0.5, 0.9),
        "TS%": (0.4, 0.7),
        "eFG%": (0.4, 0.7),
        "TO%": (0.08, 0.25),  # Smaller is better
        "AST%": (0.1, 0.4),
        "USG%": (0.15, 0.35),
        "ORB%": (0.02, 0.12),
        "DRB%": (0.15, 0.35),
        "TRB%": (0.05, 0.20),
        "off_assist": (0.1, 0.4),
        "off_to": (0.08, 0.25),  # Smaller is better
        "off_usage": (0.15, 0.35),
        "off_efg": (0.4, 0.7),
        "off_ftr": (0.2, 0.5),
        "off_threep": (0.2, 0.5),
        "off_twop": (0.4, 0.7),
        "off_twopmid": (0.2, 0.5),
        "off_twoprim": (0.2, 0.5),
        "off_orb": (0.02, 0.12),
        "def_orb": (0.15, 0.35),
        "off_reb": (0.05, 0.20),
        "def_reb": (0.15, 0.35),
        "def_stl": (0.01, 0.05),
        "def_blk": (0.01, 0.08),
        "def_fc": (0.02, 0.08),
    }

    get_stat = lambda *keys: next((safe(player.get(k)) for k in keys if player.get(k) is not None), 0)

    PPG = get_stat("PPG", "Points") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0
    RPG = get_stat("RPG", "Rebounds Total") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0
    APG = get_stat("APG", "Assists") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0
    SPG = get_stat("SPG", "Steals") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0
    BPG = get_stat("BPG", "Blocks") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0
    MPG = get_stat("MPG", "Minutes") / get_stat("Games", 1) if get_stat("Games", 1) > 0 else 0

    FG = get_stat("FieldGoals Pct", "FG%")
    ThreeP = get_stat("ThreePointFieldGoals Pct", "3P%")
    FT = get_stat("FreeThrows Pct", "FT%")
    TS = get_stat("TrueShootingPct", "TS%")
    eFG = get_stat("off_efg", "EffectiveFieldGoalPct")
    TO = get_stat("off_to", "TurnoversPct", "TO%")
    AST = get_stat("off_assist", "AssistsPct", "AST%")
    USG = get_stat("off_usage", "Usage", "USG%")
    ORB = get_stat("off_orb", "OffensiveReboundingPct", "ORB%")
    DRB = get_stat("def_orb", "DefensiveReboundingPct", "DRB%")

    off_assist = get_stat("off_assist")
    off_to_pct = get_stat("off_to")
    off_usage_pct = get_stat("off_usage")
    off_efg_pct = get_stat("off_efg")
    off_ftr_pct = get_stat("off_ftr")
    off_threep = get_stat("off_threep")
    off_twop = get_stat("off_twop")
    off_twopmid = get_stat("off_twopmid")
    off_twoprim = get_stat("off_twoprim")
    off_orb_pct = get_stat("off_orb")
    def_orb_pct = get_stat("def_orb")
    off_reb_pct = get_stat("off_reb")
    def_reb_pct = get_stat("def_reb")
    def_stl_pct = get_stat("def_stl")
    def_blk_pct = get_stat("def_blk")
    def_fc_pct = get_stat("def_fc")

    # Map stat names to their computed values
    stat_values = {
        "PPG": PPG,
        "RPG": RPG,
        "APG": APG,
        "SPG": SPG,
        "BPG": BPG,
        "MPG": MPG,
        "FG%": FG,
        "3P%": ThreeP,
        "FT%": FT,
        "TS%": TS,
        "eFG%": eFG,
        "TO%": TO,
        "AST%": AST,
        "USG%": USG,
        "ORB%": ORB,
        "DRB%": DRB,
        "off_assist": off_assist,
        "off_to": off_to_pct,
        "off_usage": off_usage_pct,
        "off_efg": off_efg_pct,
        "off_ftr": off_ftr_pct,
        "off_threep": off_threep,
        "off_twop": off_twop,
        "off_twopmid": off_twopmid,
        "off_twoprim": off_twoprim,
        "off_orb": off_orb_pct,
        "def_orb": def_orb_pct,
        "off_reb": off_reb_pct,
        "def_reb": def_reb_pct,
        "def_stl": def_stl_pct,
        "def_blk": def_blk_pct,
        "def_fc": def_fc_pct,
    }

    presets = {
        "overview": [
            {"stat": "off_assist", "value": normalize_stat(off_assist, *stat_ranges["off_assist"]), "raw": off_assist},
            {"stat": "off_twop", "value": normalize_stat(off_twop, *stat_ranges["off_twop"]), "raw": off_twop},
            {"stat": "off_threep", "value": normalize_stat(off_threep, *stat_ranges["off_threep"]), "raw": off_threep},
            {"stat": "off_orb", "value": normalize_stat(off_orb_pct, *stat_ranges["off_orb"]), "raw": off_orb_pct},
            {"stat": "def_reb", "value": normalize_stat(def_reb_pct, *stat_ranges["def_reb"]), "raw": def_reb_pct},
            {"stat": "def_stl", "value": normalize_stat(def_stl_pct, *stat_ranges["def_stl"]), "raw": def_stl_pct},
        ],
        "scoring": [
            {"stat": "off_twop", "value": normalize_stat(off_twop, *stat_ranges["off_twop"]), "raw": off_twop},
            {"stat": "off_twoprim", "value": normalize_stat(off_twoprim, *stat_ranges["off_twoprim"]), "raw": off_twoprim},
            {"stat": "off_twopmid", "value": normalize_stat(off_twopmid, *stat_ranges["off_twopmid"]), "raw": off_twopmid},
            {"stat": "off_threep", "value": normalize_stat(off_threep, *stat_ranges["off_threep"]), "raw": off_threep},
        ],
        "playmaking": [
            {"stat": "off_assist", "value": normalize_stat(off_assist, *stat_ranges["off_assist"]), "raw": off_assist},
            {"stat": "off_to", "value": invert_normalize(off_to_pct, *stat_ranges["off_to"]), "raw": off_to_pct},
            {"stat": "off_usage", "value": normalize_stat(off_usage_pct, *stat_ranges["off_usage"]), "raw": off_usage_pct},
        ],
        "defense": [
            {"stat": "def_stl", "value": normalize_stat(def_stl_pct, *stat_ranges["def_stl"]), "raw": def_stl_pct},
            {"stat": "def_blk", "value": normalize_stat(def_blk_pct, *stat_ranges["def_blk"]), "raw": def_blk_pct},
            {"stat": "def_orb", "value": normalize_stat(def_orb_pct, *stat_ranges["def_orb"]), "raw": def_orb_pct},
            {"stat": "def_reb", "value": normalize_stat(def_reb_pct, *stat_ranges["def_reb"]), "raw": def_reb_pct},
            {"stat": "def_fc", "value": invert_normalize(def_fc_pct, *stat_ranges["def_fc"]), "raw": def_fc_pct},
        ],
        "efficiency": [
            {"stat": "off_efg", "value": normalize_stat(off_efg_pct, *stat_ranges["off_efg"]), "raw": off_efg_pct},
            {"stat": "off_ftr", "value": normalize_stat(off_ftr_pct, *stat_ranges["off_ftr"]), "raw": off_ftr_pct},
            {"stat": "off_to", "value": invert_normalize(off_to_pct, *stat_ranges["off_to"]), "raw": off_to_pct},
            {"stat": "off_orb", "value": normalize_stat(off_orb_pct, *stat_ranges["off_orb"]), "raw": off_orb_pct},
            {"stat": "def_reb", "value": normalize_stat(def_reb_pct, *stat_ranges["def_reb"]), "raw": def_reb_pct},
        ],
        "perGame": [
            {"stat": "PPG", "value": normalize_stat(PPG, *stat_ranges["PPG"]), "raw": PPG},
            {"stat": "RPG", "value": normalize_stat(RPG, *stat_ranges["RPG"]), "raw": RPG},
            {"stat": "APG", "value": normalize_stat(APG, *stat_ranges["APG"]), "raw": APG},
            {"stat": "SPG", "value": normalize_stat(SPG, *stat_ranges["SPG"]), "raw": SPG},
            {"stat": "BPG", "value": normalize_stat(BPG, *stat_ranges["BPG"]), "raw": BPG},
            {"stat": "MPG", "value": normalize_stat(MPG, *stat_ranges["MPG"]), "raw": MPG},
        ],
    }

    if custom_fields:
        result = []
        for field in custom_fields:
            if field in stat_values and field in stat_ranges:
                if field in ["TO%", "off_to", "def_fc"]:
                    value = invert_normalize(stat_values[field], *stat_ranges[field])
                else:
                    value = normalize_stat(stat_values[field], *stat_ranges[field])
                result.append({"stat": field, "value": value, "raw": stat_values[field]})
        return result

    return presets.get(preset, presets["overview"])