// Player data types
export interface Player {
  AthleteSourceId: string;
  player_name: string;
  team: string;
  year: number | "career";
  is_career?: boolean;
  career_year_label?: string;
  "roster.height"?: string;
  "roster.ncaa_id": number;
  "roster.number"?: string;
  "roster.year_class"?: string;
  "roster.pos"?: string;
  "roster.origin"?: string;
  adj_rapm_margin?: number;
  off_rtg?: number;
  def_rtg?: number;
  off_usage?: number;
  off_orb?: number;
  def_orb?: number;
  off_assist?: number;
  off_to?: number;
  def_stl?: number;
  def_blk?: number;
  off_ftr?: number;
  off_threepr?: number;
  off_team_poss_pct?: number;
  conf?: string;
  posClass?: string;
  // Basic player fields (from basic player data)
  Name?: string;
  Team?: string;
  Season?: number;
  Position?: string;
  data_tier?: "basic" | "enriched";
  // Derived stats for basic players
  PPG?: number;
  APG?: number;
  RPG?: number;
  SPG?: number;
  BPG?: number;
  MPG?: number;
  // BPM values from Torvik
  BPM?: number;
  OBPM?: number;
  DBPM?: number;
}

export interface PlayerStats {
  count: number;
  filtered_count: number;
  results: Player[];
}

export interface PlayerResponse {
  player: Player;
  available_years: number[];
}

export interface Badge {
  name: string;
  level: number;
  category: string;
}

export interface PlayerMove {
  // Define based on actual move data structure
  [key: string]: any;
}

export interface SimilarPlayer {
  player: Player;
  similarity_score: number;
}

export interface RadarData {
  categories: string[];
  values: number[];
}

export interface EvolutionData {
  years: number[];
  metrics: Record<string, number[]>;
}

// API request/response types
export interface FetchPlayersParams {
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";
  year?: number | "career" | null;
  search?: string;
  dataTier?: "basic" | "enriched";
  d1Only?: boolean;
  highMajorOnly?: boolean;
  conf?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// UI state types
export type SortDirection = "asc" | "desc";
export type YearType = number | null | "career";

export interface TableState {
  sort: string;
  order: SortDirection;
  page: number;
  search: string;
  year: YearType;
}

// Environment configuration
export interface AppConfig {
  apiUrl: string;
  environment: "development" | "staging" | "production";
  features: {
    analytics: boolean;
    debugging: boolean;
  };
}
