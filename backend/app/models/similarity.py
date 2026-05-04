import numpy as np

def cosine_similarity(a, b):
    if a is None or b is None:
        return 0

    a = np.array(a)
    b = np.array(b)

    denom = (np.linalg.norm(a) * np.linalg.norm(b))

    if denom == 0:
        return 0

    return float(np.dot(a, b) / denom)

