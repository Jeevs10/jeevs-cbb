import { clsx, type ClassValue } from "clsx";

// Utility for combining Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Format utilities
export function formatYear(player: { year?: number | string | null; is_career?: boolean }): string {
  if (player.is_career || player.year === "career") return "Career";
  if (typeof player.year === "number") return player.year.toString();
  return "—";
}

export function formatNumber(value: any): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value !== "number") return String(value);
  return value.toFixed(4);
}

export function formatHeight(value: any): string {
  if (!value) return "—";
  return String(value);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  if (value === null || value === undefined || value === 0) return "—";
  return `${value.toFixed(decimals)}%`;
}

// Validation utilities
export function isValidId(id: string): boolean {
  return typeof id === "string" && id.trim().length > 0;
}

export function isValidYear(year: any): year is number | "career" | null {
  return (
    year === null ||
    year === "career" ||
    (typeof year === "number" && year > 2000 && year < 2100)
  );
}

// Search utilities
export function createSearchQuery(search: string): string {
  return search.trim().toLowerCase();
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Error handling utilities
export function handleApiError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred";
}

export function isNetworkError(error: unknown): boolean {
  return error instanceof Error && error.message.includes("Network Error");
}

// Table utilities
export function getSortIcon(
  currentSort: string,
  column: string,
  order: "asc" | "desc"
): string {
  if (currentSort !== column) return "";
  return order === "asc" ? " ↑" : " ↓";
}

export function getTableCellClasses(isSticky = false): string {
  return cn(
    "p-2 border border-black",
    isSticky && "sticky left-0 bg-[#E7E8D1] z-20 whitespace-nowrap"
  );
}

export function getTableHeaderClasses(isSortable = false): string {
  return cn(
    "p-2 border border-black select-none bg-[#B7C4A5]",
    isSortable && "cursor-pointer hover:bg-[#aab895]"
  );
}

// Data transformation utilities
export function normalizePlayerData(player: any): any {
  if (!player) return null;
  
  // Ensure numeric fields are numbers
  const numericFields = [
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
    "off_team_poss_pct"
  ];

  const normalized = { ...player };
  
  numericFields.forEach(field => {
    if (normalized[field] !== null && normalized[field] !== undefined) {
      normalized[field] = Number(normalized[field]);
    }
  });

  return normalized;
}

// Constants
export const DEFAULT_PAGE_SIZE = 50;
export const MAX_SEARCH_LENGTH = 100;
export const DEBOUNCE_DELAY = 600;

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
    "PPG",
    "APG",
    "RPG",
    "SPG",
    "BPG",
    "MPG",
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