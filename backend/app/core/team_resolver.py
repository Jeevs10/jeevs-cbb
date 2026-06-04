from typing import Union, Optional
from app.core.team_data_loader import (
    team_analytics_df,
    roster_info_df,
    historical_team_info_df,
    TEAM_LOOKUP
)
from app.core.data_loader import df as players_df
import pandas as pd

# -------------------------
# CONFIG
# -------------------------

CATEGORICAL_FIELDS = {
    "team_name",
    "conf",
    "conf_nick",
}

# -------------------------
# CORE SNAPSHOT
# -------------------------

def get_team_snapshot(team_id: str, year: Union[int, str, None] = None):
    """Get team snapshot by team ID and optional year"""
    # Convert to string for consistent lookup
    team_id_str = str(team_id)
    
    # Get historical team info
    historical_info = TEAM_LOOKUP.get(team_id_str)
    if not historical_info:
        return None
    
    # Get SourceId for analytics lookup (linking key between historical and analytics data)
    source_id = historical_info.get("SourceId")
    if source_id is None or pd.isna(source_id):
        # Return historical info only if no SourceId found
        return {
            "id": team_id_str,
            "school": historical_info.get("School"),
            "mascot": historical_info.get("Mascot"),
            "abbreviation": historical_info.get("Abbreviation"),
            "display_name": historical_info.get("DisplayName"),
            "conference": historical_info.get("Conference"),
            "primary_color": historical_info.get("PrimaryColor"),
            "secondary_color": historical_info.get("SecondaryColor"),
            "current_venue": historical_info.get("CurrentVenue"),
            "current_city": historical_info.get("CurrentCity"),
            "current_state": historical_info.get("CurrentState"),
            "analytics": None,
            "roster": [],
            "analytics_available": False,
        }
    
    source_id_str = str(source_id)
    
    # Get team analytics for the specified year using SourceId
    if year is not None:
        year_int = int(year)
        analytics = team_analytics_df[
            (team_analytics_df["_id"] == source_id_str) & 
            (team_analytics_df["year"] == year_int)
        ]
    else:
        # Get latest year
        analytics = team_analytics_df[team_analytics_df["_id"] == source_id_str]
        if not analytics.empty:
            analytics = analytics.sort_values("year").tail(1)
    
    if analytics.empty:
        # Return historical info only if no analytics found
        return {
            "id": team_id_str,
            "school": historical_info.get("School"),
            "mascot": historical_info.get("Mascot"),
            "abbreviation": historical_info.get("Abbreviation"),
            "display_name": historical_info.get("DisplayName"),
            "conference": historical_info.get("Conference"),
            "primary_color": historical_info.get("PrimaryColor"),
            "secondary_color": historical_info.get("SecondaryColor"),
            "current_venue": historical_info.get("CurrentVenue"),
            "current_city": historical_info.get("CurrentCity"),
            "current_state": historical_info.get("CurrentState"),
            "analytics": None,
            "roster": [],
            "analytics_available": False,
        }
    
    analytics_data = analytics.iloc[-1].to_dict()
    
    # Get roster info for the team and year using TeamSourceId for linking
    source_id = historical_info.get("SourceId")
    if source_id is None or pd.isna(source_id):
        roster_data = []
    else:
        source_id_str = str(source_id)
        if year is not None:
            year_int = int(year)
            # Filter by year using Season field (the CSV filename year doesn't match the Season field)
            roster = roster_info_df[
                (roster_info_df["TeamSourceId"] == source_id_str) &
                (roster_info_df["Season"].astype(str) == str(year_int))
            ]
            # Fallback: if no roster for specific year, get latest year
            if roster.empty:
                roster = roster_info_df[roster_info_df["TeamSourceId"] == source_id_str]
                if not roster.empty:
                    # Get all players from the latest season
                    roster = roster.sort_values("Season")
                    latest_season = roster["Season"].iloc[-1]
                    roster = roster[roster["Season"] == latest_season]
        else:
            # Get latest year roster
            roster = roster_info_df[roster_info_df["TeamSourceId"] == source_id_str]
            if not roster.empty:
                # Get all players from the latest season
                roster = roster.sort_values("Season")
                latest_season = roster["Season"].iloc[-1]
                roster = roster[roster["Season"] == latest_season]
        
        if roster.empty:
            roster_data = []
        else:
            # Join with player stats data
            roster_data = roster.copy()
            
            # Ensure Sourceid is string for joining
            roster_data['_join_key'] = roster_data['Sourceid'].astype(str)
            
            # Filter players by year if specified
            if year is not None:
                year_int = int(year)
                players_filtered = players_df[players_df["year"] == year_int].copy()
            else:
                # Get latest year players
                players_filtered = players_df.copy()
            
            # Use AthleteSourceId for joining (both basic and enriched have this field)
            # This matches the Sourceid in roster-info
            if 'AthleteSourceId' in players_filtered.columns:
                players_filtered['_join_key'] = players_filtered['AthleteSourceId'].astype(str)
            else:
                # Fallback: try roster.ncaa_id if AthleteSourceId not available
                players_filtered['_join_key'] = players_filtered.get('roster.ncaa_id', pd.Series()).astype(str).str.replace('.0', '', regex=False)
            
            # Select relevant stats fields to add
            stats_fields = ['_join_key', 'PPG', 'RPG', 'APG', 'PORPAG', 'Minutes', 'Points', 'Rebounds Total', 'Assists']
            available_stats_fields = [f for f in stats_fields if f in players_filtered.columns]
            players_to_join = players_filtered[available_stats_fields].copy()
            
            # Merge roster with player stats
            roster_enriched = pd.merge(
                roster_data,
                players_to_join,
                on='_join_key',
                how='left'
            )
            
            # Drop the join key
            roster_enriched = roster_enriched.drop('_join_key', axis=1)

            # Ensure Season field is preserved and properly formatted
            if 'Season' in roster_enriched.columns:
                roster_enriched['Season'] = roster_enriched['Season'].astype(str)

            # Deduplicate by player ID (Sourceid or Id) to avoid duplicates from multiple CSV files
            roster_enriched = roster_enriched.drop_duplicates(subset=['Sourceid'], keep='first')

            roster_data = roster_enriched.to_dict("records")
    
    # Combine all data and transform field names to match schema
    result = {
        "id": team_id_str,
        "school": historical_info.get("School"),
        "mascot": historical_info.get("Mascot"),
        "abbreviation": historical_info.get("Abbreviation"),
        "display_name": historical_info.get("DisplayName"),
        "conference": historical_info.get("Conference"),
        "primary_color": historical_info.get("PrimaryColor"),
        "secondary_color": historical_info.get("SecondaryColor"),
        "current_venue": historical_info.get("CurrentVenue"),
        "current_city": historical_info.get("CurrentCity"),
        "current_state": historical_info.get("CurrentState"),
        "analytics": analytics_data,
        "roster": roster_data,
        "analytics_available": True,
    }
    
    return result


def get_team_roster(team_id: str, year: Optional[Union[int, str]] = None):
    """Get roster info for a team with player stats"""
    team_id_str = str(team_id)
    
    if team_id_str not in TEAM_LOOKUP:
        return []
    
    historical_info = TEAM_LOOKUP[team_id_str]
    source_id = historical_info.get("SourceId")
    if source_id is None or pd.isna(source_id):
        return []
    
    source_id_str = str(source_id)

    if year is not None:
        year_int = int(year)
        # Filter by year using Season field (the CSV filename year doesn't match the Season field)
        roster = roster_info_df[
            (roster_info_df["TeamSourceId"] == source_id_str) &
            (roster_info_df["Season"].astype(str) == str(year_int))
        ]
    else:
        roster = roster_info_df[roster_info_df["TeamSourceId"] == source_id_str]
    
    if roster.empty:
        return []
    
    # Join with player stats data
    roster_data = roster.copy()
    
    # Ensure Sourceid is string for joining
    roster_data['_join_key'] = roster_data['Sourceid'].astype(str)
    
    # Filter players by year if specified
    if year is not None:
        year_int = int(year)
        players_filtered = players_df[players_df["year"] == year_int].copy()
    else:
        # Get latest year players
        players_filtered = players_df.copy()
    
    # Use AthleteSourceId for joining (both basic and enriched have this field)
    # This matches the Sourceid in roster-info
    if 'AthleteSourceId' in players_filtered.columns:
        players_filtered['_join_key'] = players_filtered['AthleteSourceId'].astype(str)
    else:
        # Fallback: try roster.ncaa_id if AthleteSourceId not available
        players_filtered['_join_key'] = players_filtered.get('roster.ncaa_id', pd.Series()).astype(str).str.replace('.0', '', regex=False)
    
    # Select relevant stats fields to add
    stats_fields = ['_join_key', 'PPG', 'RPG', 'APG', 'PORPAG', 'Minutes', 'Points', 'Rebounds Total', 'Assists']
    available_stats_fields = [f for f in stats_fields if f in players_filtered.columns]
    players_to_join = players_filtered[available_stats_fields].copy()
    
    # Merge roster with player stats
    roster_enriched = pd.merge(
        roster_data,
        players_to_join,
        on='_join_key',
        how='left'
    )
    
    # Drop the join key
    roster_enriched = roster_enriched.drop('_join_key', axis=1)

    # Ensure Season field is preserved and properly formatted
    if 'Season' in roster_enriched.columns:
        roster_enriched['Season'] = roster_enriched['Season'].astype(str)

    # Deduplicate by player ID (Sourceid or Id) to avoid duplicates from multiple CSV files
    roster_enriched = roster_enriched.drop_duplicates(subset=['Sourceid'], keep='first')

    return roster_enriched.to_dict("records")


def get_all_teams():
    """Get list of all teams with basic info and mini stats"""
    teams = []
    for team_id, info in TEAM_LOOKUP.items():
        # Handle NaN values by converting to None
        def safe_get(key):
            val = info.get(key)
            if pd.isna(val):
                return None
            return val
        
        # Get SourceId for analytics lookup
        source_id = safe_get("SourceId")
        mini_stats = None
        
        if source_id is not None:
            source_id_str = str(source_id)
            # Get latest analytics for this team
            analytics = team_analytics_df[team_analytics_df["_id"] == source_id_str]
            if not analytics.empty:
                analytics = analytics.sort_values("year").tail(1)
                analytics_data = analytics.iloc[-1].to_dict()
                mini_stats = {
                    "wins": analytics_data.get("wins"),
                    "losses": analytics_data.get("losses"),
                    "adj_net": analytics_data.get("adj_net"),
                    "off_adj_ppp": analytics_data.get("off_adj_ppp"),
                    "def_adj_ppp": analytics_data.get("def_adj_ppp"),
                    "wab": analytics_data.get("wab"),
                    "rank_adj_net": analytics_data.get("rank_adj_net"),
                    "rank_off_adj_ppp": analytics_data.get("rank_off_adj_ppp"),
                    "rank_def_adj_ppp": analytics_data.get("rank_def_adj_ppp"),
                    "rank_wab": analytics_data.get("rank_wab"),
                }
        
        teams.append({
            "id": team_id,
            "school": safe_get("School"),
            "mascot": safe_get("Mascot"),
            "abbreviation": safe_get("Abbreviation"),
            "display_name": safe_get("DisplayName"),
            "conference": safe_get("Conference"),
            "mini_stats": mini_stats,
        })
    return teams


def get_team_by_name(team_name: str):
    """Get team by name (partial match)"""
    team_name_lower = team_name.lower()
    
    for team_id, info in TEAM_LOOKUP.items():
        if team_name_lower in info.get("School", "").lower() or \
           team_name_lower in info.get("DisplayName", "").lower() or \
           team_name_lower in info.get("Abbreviation", "").lower():
            return get_team_snapshot(team_id)
    
    return None
