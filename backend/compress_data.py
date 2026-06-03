"""Compress CSV files to gzip to reduce file size for Git and deployment."""

import gzip
import shutil
from pathlib import Path
import os

DATA_DIR = Path(__file__).parent / "data"

# Files to compress (over 1MB or important large files)
FILES_TO_COMPRESS = [
    # Aggregate files
    "aggregate/all_players.csv",
    
    # Player files (enriched files are largest)
    "players/2019-players_enriched.csv",
    "players/2020-players_enriched.csv",
    "players/2021-players_enriched.csv",
    "players/2022-players_enriched.csv",
    "players/2023-players_enriched.csv",
    "players/2024-players_enriched.csv",
    "players/2025-players_enriched.csv",
    "players/2026-players_enriched.csv",
    
    # Large player CSV files
    "players/2019-players.csv",
    "players/2020-players.csv",
    "players/2021-players.csv",
    "players/2022-players.csv",
    "players/2023-players.csv",
    "players/2024-players.csv",
    "players/2025-players.csv",
    "players/2026-players.csv",
    
    # Cluster files
    "player_clusters.csv",
    "player_clusters_unified.csv",
    
    # Projection files
    "bpm_projections_2027.csv",
    "bpm_change_modeling_data.csv",
    
    # Team files
    "teams/2019-hoop-explorer-teams.csv",
    "teams/2020-hoop-explorer-teams.csv",
    "teams/2021-hoop-explorer-teams.csv",
    "teams/2022-hoop-explorer-teams.csv",
    "teams/2023-hoop-explorer-teams.csv",
    "teams/2024-hoop-explorer-teams.csv",
    "teams/2025-hoop-explorer-teams.csv",
    "teams/2026-hoop-explorer-teams.csv",
]

def compress_file(input_path: Path, output_path: Path):
    """Compress a file using gzip."""
    if not input_path.exists():
        print(f"  Skipping {input_path} (not found)")
        return
    
    print(f"  Compressing {input_path.name}...")
    
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    original_size = input_path.stat().st_size
    compressed_size = output_path.stat().st_size
    ratio = (1 - compressed_size / original_size) * 100
    
    print(f"    Original: {original_size / 1024 / 1024:.2f} MB")
    print(f"    Compressed: {compressed_size / 1024 / 1024:.2f} MB")
    print(f"    Reduction: {ratio:.1f}%")

def decompress_file(input_path: Path, output_path: Path):
    """Decompress a gzip file."""
    if not input_path.exists():
        print(f"  Skipping {input_path} (not found)")
        return
    
    print(f"  Decompressing {input_path.name}...")
    
    with gzip.open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"    Decompressed to {output_path}")

def main():
    print("Compressing CSV files...")
    
    for file_path in FILES_TO_COMPRESS:
        input_file = DATA_DIR / file_path
        output_file = DATA_DIR / f"{file_path}.gz"
        
        compress_file(input_file, output_file)
    
    print("\n✅ Compression complete!")
    print("\nNext steps:")
    print("1. Update .gitignore to ignore uncompressed CSV files")
    print("2. Commit the .gz files instead")
    print("3. Update data_loader.py to read from .gz files")
    print("4. Optionally delete original CSV files after confirming .gz files work")

def decompress_all():
    """Decompress all .gz files back to CSV."""
    print("Decompressing CSV files...")
    
    for file_path in FILES_TO_COMPRESS:
        input_file = DATA_DIR / f"{file_path}.gz"
        output_file = DATA_DIR / file_path
        
        decompress_file(input_file, output_file)
    
    print("\n✅ Decompression complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--decompress":
        decompress_all()
    else:
        main()
