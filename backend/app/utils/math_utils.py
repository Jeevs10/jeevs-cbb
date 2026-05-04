def safe(v):
    try:
        if v is None:
            return 0
        return float(v)
    except:
        return 0