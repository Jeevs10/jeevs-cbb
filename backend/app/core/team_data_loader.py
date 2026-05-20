import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_team_analytics():
    """Load team analytics data (hoop explorer data)"""
    try:
        dfs = []
        
        # Load all available years (2019-2026)
        for year in range(2019, 2027):
            csv_path = os.path.join(BASE_DIR, "data", f"{year}-hoop-explorer-teams.csv")
            if os.path.exists(csv_path):
                df_year = pd.read_csv(csv_path, encoding='utf-8-sig')
                df_year["year"] = year
                if '_id' in df_year.columns:
                    df_year['_id'] = df_year['_id'].astype(str)
                dfs.append(df_year)
                print(f"Loaded {year} team analytics: {len(df_year)} teams")
        
        if not dfs:
            print(f"Warning: No team analytics files found")
            return pd.DataFrame()
        
        # Combine all years
        df_combined = pd.concat(dfs, ignore_index=True)
        
        print(f"Loaded total team analytics: {len(df_combined)} entries across {len(dfs)} years")
        
        return df_combined
    except Exception as e:
        print(f"Error loading team analytics: {e}")
        return pd.DataFrame()

def load_roster_info():
    """Load roster info for teams"""
    try:
        dfs = []
        
        # Load all available years (2019-2026)
        for year in range(2019, 2027):
            csv_path = os.path.join(BASE_DIR, "data", f"{year}-roster-info.csv")
            if os.path.exists(csv_path):
                df_year = pd.read_csv(csv_path)
                df_year["Season"] = df_year["Season"].astype(str)
                # Convert Season to year (e.g., "2025" -> 2025)
                df_year["year"] = pd.to_numeric(df_year["Season"], errors='coerce')
                if 'TeamSourceId' in df_year.columns:
                    df_year['TeamSourceId'] = df_year['TeamSourceId'].astype(str)
                dfs.append(df_year)
                print(f"Loaded {year} roster info: {len(df_year)} entries")
        
        if not dfs:
            print(f"Warning: No roster info files found")
            return pd.DataFrame()
        
        # Combine all years
        df_combined = pd.concat(dfs, ignore_index=True)
        
        print(f"Loaded total roster info: {len(df_combined)} entries across {len(dfs)} years")
        
        return df_combined
    except Exception as e:
        print(f"Error loading roster info: {e}")
        return pd.DataFrame()

def load_historical_team_info():
    """Load static historical team information"""
    try:
        csv = os.path.join(BASE_DIR, "data", "historical-team-info.csv")
        
        if not os.path.exists(csv):
            print(f"Warning: Historical team info file not found at {csv}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv, encoding='utf-8-sig')  # Handle BOM
        
        # Ensure Id is string type for consistent lookup
        if 'Id' in df.columns:
            df['Id'] = df['Id'].astype(str)
        
        print(f"Loaded historical team info: {len(df)} teams")
        print(f"Sample IDs: {df['Id'].head().tolist()}")
        
        return df
    except Exception as e:
        print(f"Error loading historical team info: {e}")
        return pd.DataFrame()

# Load all team data
team_analytics_df = load_team_analytics()
roster_info_df = load_roster_info()
historical_team_info_df = load_historical_team_info()

# Create team lookup dictionaries
TEAM_LOOKUP = {}

if not historical_team_info_df.empty:
    TEAM_LOOKUP = historical_team_info_df.set_index("Id").to_dict("index")
else:
    print("Warning: Historical team info is empty, TEAM_LOOKUP will be empty")

# Note: TEAM_ANALYTICS_LOOKUP is not created since we now have multiple years of data
# Use team_analytics_df directly with year filtering instead
