"""Clear the player vectors cache to force a rebuild on next server start."""

import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "app", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "player_vectors_cache.pkl")
CACHE_METADATA_FILE = os.path.join(CACHE_DIR, "player_vectors_cache_metadata.json")

print("Clearing player vectors cache...")

if os.path.exists(CACHE_FILE):
    os.remove(CACHE_FILE)
    print(f"Removed {CACHE_FILE}")
else:
    print(f"Cache file not found: {CACHE_FILE}")

if os.path.exists(CACHE_METADATA_FILE):
    os.remove(CACHE_METADATA_FILE)
    print(f"Removed {CACHE_METADATA_FILE}")
else:
    print(f"Metadata file not found: {CACHE_METADATA_FILE}")

print("\nCache cleared. Restart the server to rebuild with new BPM values.")
