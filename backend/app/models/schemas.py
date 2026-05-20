from typing import List, Optional, Union
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
    MPG: Optional[float] = None
    # Shooting and usage fields
    off_efg: Optional[float] = None
    TrueShootingPct: Optional[float] = None
    Usage: Optional[float] = None
    # Additional stats fields
    NetRating: Optional[float] = None
    adj_prod_margin: Optional[float] = None
    FreeThrows_Pct: Optional[float] = Field(None, alias="FreeThrows Pct")

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

# Health check model
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
