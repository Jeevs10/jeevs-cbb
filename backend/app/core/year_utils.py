# app/core/year_utils.py

def normalize_year(year):
    if year is None:
        return None

    if isinstance(year, str) and year.lower() == "career":
        return "career"

    try:
        return int(year)
    except:
        return None