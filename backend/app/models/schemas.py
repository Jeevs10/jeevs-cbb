from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator

# Base response model
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

# Error response model
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: Optional[str] = None

# Player-related models
class PlayerBase(BaseModel):
    player_name: str
    team: str
    year: Union[int, str]
    adj_rapm_margin: Optional[float] = None
    off_rtg: Optional[float] = None
    def_rtg: Optional[float] = None
    off_usage: Optional[float] = None
    off_orb: Optional[float] = None
    def_orb: Optional[float] = None
    off_assist: Optional[float] = None
    off_to: Optional[float] = None
    def_stl: Optional[float] = None
    def_blk: Optional[float] = None
    off_ftr: Optional[float] = None
    off_threepr: Optional[float] = None
    off_team_poss_pct: Optional[float] = None
    Height: Optional[float] = None
    Weight: Optional[float] = None
    HometownCity: Optional[str] = None
    HometownState: Optional[str] = None
    HometownCountry: Optional[str] = None

class Player(PlayerBase):
    AthleteSourceId: Union[str, int, float]
    roster: Optional[dict] = None
    conf: Optional[str] = None
    posClass: Optional[str] = None
    is_career: Optional[bool] = False
    data_tier: Optional[str] = None
    Position: Optional[str] = None
    # Basic stats fields
    Games: Optional[float] = None
    Minutes: Optional[float] = None
    Points: Optional[float] = None
    Assists: Optional[float] = None
    Rebounds_Total: Optional[float] = Field(None, alias="Rebounds Total")
    Rebounds_Offensive: Optional[float] = Field(None, alias="Rebounds Offensive")
    Rebounds_Defensive: Optional[float] = Field(None, alias="Rebounds Defensive")
    Steals: Optional[float] = None
    Blocks: Optional[float] = None
    # Derived stats fields
    PPG: Optional[float] = None
    APG: Optional[float] = None
    RPG: Optional[float] = None
    SPG: Optional[float] = None
    BPG: Optional[float] = None
    BPM: Optional[float] = None
    OBPM: Optional[float] = None
    DBPM: Optional[float] = None
    VORP: Optional[float] = None
    MPG: Optional[float] = None
    # Shooting and usage fields
    off_efg: Optional[float] = None
    TrueShootingPct: Optional[float] = None
    Usage: Optional[float] = None
    # Additional stats fields
    NetRating: Optional[float] = None
    adj_prod_margin: Optional[float] = None
    FreeThrows_Pct: Optional[float] = Field(None, alias="FreeThrows Pct")
    # Move-specific fields
    off_style_rim_attack_ppp: Optional[float] = None
    off_style_rim_attack_pct: Optional[float] = None
    off_style_rim_attack_usg: Optional[float] = None
    off_style_perimeter_sniper_ppp: Optional[float] = None
    off_style_perimeter_sniper_pct: Optional[float] = None
    off_style_perimeter_sniper_usg: Optional[float] = None
    off_style_mid_range_ppp: Optional[float] = None
    off_style_mid_range_pct: Optional[float] = None
    off_style_mid_range_usg: Optional[float] = None
    off_style_transition_ppp: Optional[float] = None
    off_style_transition_pct: Optional[float] = None
    off_style_transition_usg: Optional[float] = None
    off_style_pnr_passer_ppp: Optional[float] = None
    off_style_pnr_passer_pct: Optional[float] = None
    off_style_pnr_passer_usg: Optional[float] = None
    off_style_post_up_ppp: Optional[float] = None
    off_style_post_up_pct: Optional[float] = None
    off_style_post_up_usg: Optional[float] = None
    # Move percentile fields
    pctile_off_style_rim_attack_pct: Optional[float] = None
    pctile_off_style_rim_attack_ppp: Optional[float] = None
    pctile_off_style_perimeter_sniper_pct: Optional[float] = None
    pctile_off_style_perimeter_sniper_ppp: Optional[float] = None
    pctile_off_style_mid_range_pct: Optional[float] = None
    pctile_off_style_mid_range_ppp: Optional[float] = None
    pctile_off_style_transition_pct: Optional[float] = None
    pctile_off_style_transition_ppp: Optional[float] = None
    pctile_off_style_pnr_passer_pct: Optional[float] = None
    pctile_off_style_pnr_passer_ppp: Optional[float] = None
    pctile_off_style_post_up_pct: Optional[float] = None
    pctile_off_style_post_up_ppp: Optional[float] = None

class PlayerListResponse(BaseResponse):
    count: int
    filtered_count: int
    results: List[Player]

class PlayerResponse(BaseResponse):
    player: Player
    available_years: List[int]

# Query parameter models
class PlayerQueryParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort: str = Field(default="adj_rapm_margin")
    order: str = Field(default="desc", pattern="^(asc|desc)$")
    year: Optional[Union[int, str]] = Field(default=None)
    conf: Optional[str] = Field(default=None)
    search: Optional[str] = Field(default=None)
    dataTier: Optional[str] = Field(default=None, pattern="^(basic|enriched)$")
    d1Only: Optional[bool] = Field(default=False)
    highMajorOnly: Optional[bool] = Field(default=False)

    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 100:
                raise ValueError('Search term too long')
        return v

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v is not None and v != "career":
            try:
                year_int = int(v)
                if year_int < 2000 or year_int > 2100:
                    raise ValueError('Year must be between 2000 and 2100')
                return year_int
            except ValueError:
                raise ValueError('Year must be a valid integer or "career"')
        return v

# Badge models
class Badge(BaseModel):
    name: str
    level: int
    category: str

class BadgeResponse(BaseResponse):
    badges: List[Badge]

# Team-related models
class MiniStats(BaseModel):
    wins: Optional[float] = None
    losses: Optional[float] = None
    adj_net: Optional[float] = None
    off_adj_ppp: Optional[float] = None
    def_adj_ppp: Optional[float] = None
    wab: Optional[float] = None
    rank_adj_net: Optional[float] = None
    rank_off_adj_ppp: Optional[float] = None
    rank_def_adj_ppp: Optional[float] = None
    rank_wab: Optional[float] = None

class TeamBase(BaseModel):
    id: str
    school: str
    mascot: Optional[str] = None
    abbreviation: Optional[str] = None
    display_name: Optional[str] = None
    conference: Optional[str] = None
    mini_stats: Optional[MiniStats] = None

class Team(TeamBase):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    current_venue: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    analytics: Optional[Dict[str, Any]] = None
    roster: Optional[List[Dict[str, Any]]] = None
    analytics_available: Optional[bool] = True

class TeamListResponse(BaseResponse):
    count: int
    results: List[TeamBase]

class TeamResponse(BaseResponse):
    team: Team
    available_years: List[int]

# NIL valuation models
class NilBreakdown(BaseModel):
    position_rank: Optional[float] = None
    win_shares: Optional[float] = None
    bpm_percentile: Optional[float] = None
    team_success: Optional[float] = None
    conference_prestige: Optional[float] = None
    cluster_quality: Optional[float] = None
    total_score: Optional[float] = None

class NilValuation(BaseModel):
    ncaa_id: str
    player_name: str
    team: str
    position: str
    year: str
    nil_score: Optional[float] = None
    estimated_value_low: Optional[float] = None
    estimated_value_high: Optional[float] = None
    percentile_all: Optional[float] = None
    percentile_position: Optional[float] = None
    cluster_id: Optional[Union[int, str]] = None
    cluster_description: Optional[str] = None
    breakdown: Optional[NilBreakdown] = None

class NilValuationResponse(BaseResponse):
    valuation: NilValuation

class TeamNilResponse(BaseResponse):
    team_id: str
    team_name: str
    year: str
    total_team_value: Optional[float] = None
    valuations: List[NilValuation]

class NilListResponse(BaseResponse):
    count: int
    filtered_count: int
    results: List[NilValuation]

# Health check model
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# Projection models
class ClusterDescription(BaseModel):
    cluster_id: int
    name: Optional[str] = None
    count: int
    avg_height: float
    avg_usage: float
    avg_rim_freq: float
    avg_3pt_pct: float
    avg_bpm: float
    top_players: List[Dict[str, Any]]

class ProjectionYear(BaseModel):
    year: int
    projected_bpm: Optional[float] = None
    bpm_change: Optional[float] = None
    confidence_interval: Optional[List[float]] = None
    percentile_rank: Optional[float] = None
    sample_size: Optional[int] = None
    error: Optional[str] = None

class SimilarPlayer(BaseModel):
    player_key: str
    player_name: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    bpm_change: Optional[float] = None
    similarity: float
    career_bpm: Optional[List[Dict[str, Any]]] = None

class ClusterTransition(BaseModel):
    cluster_id: int
    probability: float
    name: Optional[str] = None
    avg_bpm: float
    avg_usage: float
    avg_height: float

class ClusterTransitions(BaseModel):
    current_cluster_id: int
    stay_probability: float
    destinations: List[ClusterTransition]

class ProjectionResponse(BaseResponse):
    player_id: str
    current_year: int
    cluster_id: int
    cluster_description: Optional[ClusterDescription] = None
    historical_samples: int
    projections: List[ProjectionYear]
    similar_players: List[SimilarPlayer]
    cluster_transitions: Optional[ClusterTransitions] = None
    methodology: str
