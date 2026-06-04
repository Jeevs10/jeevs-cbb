import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_team_analytics():
    """Load team analytics data (hoop explorer data)"""
    try:
        dfs = []
        
        # Load all available years (2019-2026)
        for year in range(2019, 2027):
            csv_path = os.path.join(BASE_DIR, "data", "teams", f"{year}-hoop-explorer-teams.csv")
            if os.path.exists(csv_path):
                df_year = pd.read_csv(csv_path, encoding='utf-8-sig')
                df_year["year"] = year
                if '_id' in df_year.columns:
                    df_year['_id'] = df_year['_id'].astype(str)
                dfs.append(df_year)
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine all years
        df_combined = pd.concat(dfs, ignore_index=True)
        
        
        return df_combined
    except Exception as e:
        return pd.DataFrame()

def load_roster_info():
    """Load roster info for teams"""
    try:
        dfs = []
        
        # Load all available years (2019-2026)
        for year in range(2019, 2027):
            csv_path = os.path.join(BASE_DIR, "data", "players", f"{year}-roster-info.csv")
            if os.path.exists(csv_path):
                df_year = pd.read_csv(csv_path)
                df_year["Season"] = df_year["Season"].astype(str)
                # Convert Season to year (e.g., "2025" -> 2025)
                df_year["year"] = pd.to_numeric(df_year["Season"], errors='coerce')
                if 'TeamSourceId' in df_year.columns:
                    df_year['TeamSourceId'] = df_year['TeamSourceId'].astype(str)
                dfs.append(df_year)
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine all years
        df_combined = pd.concat(dfs, ignore_index=True)
        
        
        return df_combined
    except Exception as e:
        return pd.DataFrame()

def load_historical_team_info():
    """Load static historical team information"""
    try:
        csv = os.path.join(BASE_DIR, "data", "teams", "historical-team-info.csv")
        
        if not os.path.exists(csv):
            return pd.DataFrame()
        
        df = pd.read_csv(csv, encoding='utf-8-sig')  # Handle BOM
        
        # Ensure Id is string type for consistent lookup
        if 'Id' in df.columns:
            df['Id'] = df['Id'].astype(str)
        
        
        return df
    except Exception as e:
        return pd.DataFrame()

# Load all team data
team_analytics_df = load_team_analytics()
roster_info_df = load_roster_info()
historical_team_info_df = load_historical_team_info()

# Create team lookup dictionaries
TEAM_LOOKUP = {}

if not historical_team_info_df.empty:
    TEAM_LOOKUP = historical_team_info_df.set_index("Id").to_dict("index")

# Note: TEAM_ANALYTICS_LOOKUP is not created since we now have multiple years of data
# Use team_analytics_df directly with year filtering instead
