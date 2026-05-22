import { AppConfig } from "@/types";

export const config: AppConfig = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  environment: (process.env.NODE_ENV as "development" | "staging" | "production") || "development",
  features: {
    analytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === "true",
    debugging: process.env.NODE_ENV === "development",
  },
};

// API endpoints
export const API_ENDPOINTS = {
  players: "/api/v1/players",
  player: (id: string) => `/api/v1/players/${id}`,
  playerMoves: (id: string) => `/api/v1/players/${id}/moves`,
  playerBadges: (id: string) => `/api/v1/players/${id}/badges`,
  playerSimilar: (id: string) => `/api/v1/players/${id}/similar`,
  playerRadar: (id: string) => `/api/v1/players/${id}/radar`,
  playerEvolution: (id: string) => `/api/v1/players/${id}/evolution`,
  years: "/api/v1/years",
  teams: "/api/v1/teams",
  team: (id: string) => `/api/v1/teams/${id}`,
  movesRankings: "/api/v1/moves/rankings",
} as const;

// Pagination defaults
export const PAGINATION = {
  DEFAULT_LIMIT: 50,
  DEFAULT_PAGE: 0,
} as const;

// Table configuration
export const TABLE_CONFIG = {
  SORTABLE_COLUMNS: new Set([
    "year",
    "adj_rapm_margin",
    "off_rtg",
    "def_rtg",
    "off_usage",
    "off_orb",
    "def_orb",
    "off_assist",
    "off_to",
    "def_stl",
    "def_blk",
    "off_ftr",
    "off_threepr",
    "roster.height",
    "off_team_poss_pct",
  ]),
  PERCENTAGE_COLUMNS: new Set([
    "off_usage",
    "off_assist",
    "off_to",
    "off_orb",
    "def_orb",
    "off_ftr",
    "def_stl",
    "def_blk",
    "off_threepr",
  ]),
} as const;
