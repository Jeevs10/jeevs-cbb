const BASE_URL = "http://localhost:8000";

// -------------------------
// TYPE (IMPORTANT)
// -------------------------
type YearParam = number | null | "career";

// -------------------------
// PLAYER
// -------------------------
export async function fetchPlayer(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}`);

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
// ALL PLAYERS
// -------------------------
export async function fetchAllPlayers({
  limit = 50,
  offset = 0,
  sort = "adj_rapm_margin",
  order = "desc",
  year,
  search,   // 🔥 ADD THIS
}: {
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";
  year?: number | null;
  search?: string;   // 🔥 ADD THIS
}) {
  const url = new URL(`${BASE_URL}/api/v1/players`);

  url.searchParams.append("limit", String(limit));
  url.searchParams.append("offset", String(offset));
  url.searchParams.append("sort", sort);
  url.searchParams.append("order", order);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  if (search && search.trim()) {
    url.searchParams.append("search", search.trim());
  }

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch players");

  const data = await res.json();
  return data.results;
}

// -------------------------
// MOVES
// -------------------------
export async function fetchPlayerMoves(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/moves`);

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
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/badges`);

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
export async function fetchPlayerSimilar(id: string, styleWeight = 0.7, year?: YearParam) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/similar`);

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
export async function fetchPlayerRadar(id: string, year?: YearParam, preset?: string, custom_fields?: string[]) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/radar`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }
  if (preset) {
    url.searchParams.append("preset", preset);
  }
  if (custom_fields && custom_fields.length > 0) {
    custom_fields.forEach(field => {
      url.searchParams.append("custom_fields", field);
    });
  }

  const res = await fetch(url.toString());

  if (!res.ok) throw new Error("Failed to fetch radar");

  return res.json();
}

export async function fetchPlayerEvolution(
  id: string,
  year?: YearParam,
  metric?: string
) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/evolution`);

  // 🔥 OPTIONAL: decide behavior
  // If you want cross-era ALWAYS → comment this out
  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  if (metric) {
    url.searchParams.append("metric", metric);
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch player evolution");
  }

  return res.json();
}

// -------------------------
// HISTORY
// -------------------------
export async function fetchPlayerHistory(id: string) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/history`);

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch player history");
  }

  return res.json();
}

// -------------------------
// YEARS
// -------------------------
export async function fetchYears() {
  const url = new URL(`${BASE_URL}/api/v1/years`);
  
  const res = await fetch(url.toString());
  
  if (!res.ok) {
    throw new Error("Failed to fetch years");
  }
  
  return res.json();
}

// -------------------------
// TEAMS
// -------------------------
export async function fetchTeam(id: string, year?: YearParam) {
  const url = new URL(`${BASE_URL}/api/v1/teams/${id}`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch team");
  }

  return res.json();
}

export async function fetchAllTeams(year?: YearParam) {
  const url = new URL(`${BASE_URL}/api/v1/teams`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch teams");
  }

  return res.json();
}

// -------------------------
// PLAYER GAMES
// -------------------------
export async function fetchPlayerGames(id: string, year?: YearParam, limit: number = 5) {
  const url = new URL(`${BASE_URL}/api/v1/players/${id}/games`);

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
  }

  url.searchParams.append("limit", String(limit));

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error("Failed to fetch player games");
  }

  return res.json();
}