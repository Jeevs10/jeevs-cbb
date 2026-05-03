export async function fetchPlayer(id: string) {
  const res = await fetch(`http://localhost:8000/players/${id}`);
  if (!res.ok) throw new Error("Failed to fetch player");
  return res.json();
}

