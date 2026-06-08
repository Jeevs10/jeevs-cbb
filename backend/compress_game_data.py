"""Compress game data JSON files to gzip to reduce file size for Git and deployment."""

import gzip
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
GAMES_DIR = DATA_DIR / "games"

def compress_json_files():
    """Compress all JSON files in the games directory."""
    print("Compressing game data JSON files...")
    
    json_files = sorted(GAMES_DIR.glob("*.json"))
    
    for json_file in json_files:
        if json_file.name.endswith('.gz'):
            continue
        
        gz_file = json_file.with_suffix('.json.gz')
        
        print(f"  Compressing {json_file.name}...")
        
        with open(json_file, 'rb') as f_in:
            with gzip.open(gz_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        original_size = json_file.stat().st_size
        compressed_size = gz_file.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100
        
        print(f"    Original: {original_size / 1024 / 1024:.2f} MB")
        print(f"    Compressed: {compressed_size / 1024 / 1024:.2f} MB")
        print(f"    Reduction: {ratio:.1f}%")
    
    print("\n✅ Compression complete!")

if __name__ == "__main__":
    compress_json_files()
