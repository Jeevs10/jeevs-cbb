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
// ALL PLAYERS
// -------------------------
export async function fetchAllPlayers({
  limit = 50,
  offset = 0,
  sort = "adj_rapm_margin",
  order = "desc",   // 🔥 ADD THIS
  year,
}: {
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";   // 🔥 ADD THIS
  year?: YearParam;
}) {
  const url = new URL(`${BASE_URL}/players`);

  url.searchParams.append("limit", String(limit));
  url.searchParams.append("offset", String(offset));
  url.searchParams.append("sort", sort);
  url.searchParams.append("order", order); // 🔥 CRITICAL FIX

  if (year !== undefined && year !== null) {
    url.searchParams.append("year", String(year));
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