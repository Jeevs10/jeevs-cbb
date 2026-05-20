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
    }

    # Get basic stats with fallbacks for different naming conventions
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
    }

    # Define presets with their field sets
    presets = {
        "overview": [
            {"stat": "PPG", "value": normalize_stat(PPG, *stat_ranges["PPG"])},
            {"stat": "RPG", "value": normalize_stat(RPG, *stat_ranges["RPG"])},
            {"stat": "APG", "value": normalize_stat(APG, *stat_ranges["APG"])},
            {"stat": "SPG", "value": normalize_stat(SPG, *stat_ranges["SPG"])},
            {"stat": "BPG", "value": normalize_stat(BPG, *stat_ranges["BPG"])},
            {"stat": "MPG", "value": normalize_stat(MPG, *stat_ranges["MPG"])},
        ],
        "scoring": [
            {"stat": "PPG", "value": normalize_stat(PPG, *stat_ranges["PPG"])},
            {"stat": "FG%", "value": normalize_stat(FG, *stat_ranges["FG%"])},
            {"stat": "3P%", "value": normalize_stat(ThreeP, *stat_ranges["3P%"])},
            {"stat": "FT%", "value": normalize_stat(FT, *stat_ranges["FT%"])},
            {"stat": "TS%", "value": normalize_stat(TS, *stat_ranges["TS%"])},
        ],
        "playmaking": [
            {"stat": "APG", "value": normalize_stat(APG, *stat_ranges["APG"])},
            {"stat": "AST%", "value": normalize_stat(AST, *stat_ranges["AST%"])},
            {"stat": "TO%", "value": invert_normalize(TO, *stat_ranges["TO%"])},  # Inverted - smaller is better
            {"stat": "USG%", "value": normalize_stat(USG, *stat_ranges["USG%"])},
        ],
        "defense": [
            {"stat": "SPG", "value": normalize_stat(SPG, *stat_ranges["SPG"])},
            {"stat": "BPG", "value": normalize_stat(BPG, *stat_ranges["BPG"])},
            {"stat": "DRB%", "value": normalize_stat(DRB, *stat_ranges["DRB%"])},
            {"stat": "RPG", "value": normalize_stat(RPG, *stat_ranges["RPG"])},
        ],
        "efficiency": [
            {"stat": "TS%", "value": normalize_stat(TS, *stat_ranges["TS%"])},
            {"stat": "eFG%", "value": normalize_stat(eFG, *stat_ranges["eFG%"])},
            {"stat": "TO%", "value": invert_normalize(TO, *stat_ranges["TO%"])},  # Inverted - smaller is better
            {"stat": "AST%", "value": normalize_stat(AST, *stat_ranges["AST%"])},
        ],
    }

    # Handle custom field selection
    if custom_fields:
        result = []
        for field in custom_fields:
            if field in stat_values and field in stat_ranges:
                if field == "TO%":
                    value = invert_normalize(stat_values[field], *stat_ranges[field])
                else:
                    value = normalize_stat(stat_values[field], *stat_ranges[field])
                result.append({"stat": field, "value": value})
        return result

    return presets.get(preset, presets["overview"])