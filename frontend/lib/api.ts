const BASE_URL = "http://localhost:8000";

// -------------------------
// TYPE (IMPORTANT)
// -------------------------
type YearParam = number | null | "career";

// -------------------------
// PLAYER
// -------------------------
export async function fetchPlayer(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/players/${id}`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch player");
  }

  return res.json();
}

// -------------------------
// ALL PLAYERS (LISTING)
// -------------------------
export async function fetchAllPlayers({
  limit = 50,
  offset = 0,
  sort = "adj_rapm_margin",
  order = "desc",
  year,
  conf,
  search,
}: {
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";
  year?: YearParam;
  conf?: string;
  search?: string;
}): Promise<Player[]> {
  // Use the working test endpoint for now
  const url = new URL(`${BASE_URL}/players`);

  url.searchParams.append("limit", String(limit));

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch players");

  const data: any = await res.json();
  return data.results || [];
}

// -------------------------
// SEARCH PLAYERS
// -------------------------
export async function searchPlayers({
  q,
  limit = 50,
  offset = 0,
  sort = "adj_rapm_margin",
  order = "desc",
  year,
  conf,
}: {
  q: string;
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";
  year?: YearParam;
  conf?: string;
}): Promise<SearchResponse> {
  const url = new URL(`${BASE_URL}/search`);

  url.searchParams.append("q", q);
  url.searchParams.append("limit", String(limit));
  url.searchParams.append("offset", String(offset));
  url.searchParams.append("sort", sort);
  url.searchParams.append("order", order);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  if (conf) {
    url.searchParams.append("conf", conf.trim());
  }

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to search players");

  return res.json();
}

// -------------------------
// SEARCH SUGGESTIONS
// -------------------------
export async function fetchSearchSuggestions({
  q,
  limit = 10,
}: {
  q: string;
  limit?: number;
}): Promise<SearchSuggestionsResponse> {
  const url = new URL(`${BASE_URL}/search/suggestions`);

  url.searchParams.append("q", q);
  url.searchParams.append("limit", String(limit));

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch search suggestions");

  return res.json();
}

// -------------------------
// MOVES
// -------------------------
export async function fetchPlayerMoves(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/players/${id}/moves`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch moves");

  return res.json();
}

// -------------------------
// BADGES
// -------------------------
export async function fetchPlayerBadges(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/players/${id}/badges`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch badges");

  return res.json();
}

// -------------------------
// SIMILAR PLAYERS
// -------------------------
export async function fetchSimilarPlayers(
  id: string,
  styleWeight = 0.7,
  year?: YearParam
) {
  const url = new URL(`${BASE_URL}/players/${id}/similar`);

  url.searchParams.append("style_weight", String(styleWeight));

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch similar players");

  return res.json();
}

// -------------------------
// RADAR
// -------------------------
export async function fetchPlayerRadar(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/players/${id}/radar`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch radar");

  return res.json();
}

export async function fetchPlayerEvolution(
  id: string,
  year?: YearParam
) {
  const url = new URL(`${BASE_URL}/players/${id}/evolution`);

  // 🔥 OPTIONAL: decide behavior
  // If you want cross-era ALWAYS → comment this out
  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch player evolution");
  }

  return res.json();
}