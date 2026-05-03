"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function Home() {
  const [players, setPlayers] = useState<any[]>([]);
  const [sort, setSort] = useState("adj_rapm_margin");
  const [page, setPage] = useState(0);

  const limit = 50;

  useEffect(() => {
    fetch(
      `http://localhost:8000/players?limit=${limit}&offset=${page * limit}&sort=${sort}`
    )
      .then((res) => res.json())
      .then((data) => setPlayers(data.results));
  }, [sort, page]);

  return (
    <div style={{ padding: 20 }}>
      <h1>Player Leaderboard</h1>

      {/* SORT CONTROLS */}
      <div style={{ marginBottom: 10 }}>
        <button onClick={() => setSort("adj_rapm_margin")}>
          RAPM Margin
        </button>
        <button onClick={() => setSort("off_rtg")}>Off Rating</button>
        <button onClick={() => setSort("def_rtg")}>Def Rating</button>
        <button onClick={() => setSort("off_usage")}>Usage</button>
      </div>

      {/* TABLE */}
      <table border={1} cellPadding={10}>
        <thead>
          <tr>
            <th>Player</th>
            <th>Team</th>
            <th>Off RTG</th>
            <th>Def RTG</th>
            <th>RAPM</th>
          </tr>
        </thead>

        <tbody>
          {players.map((p) => (
            <tr key={p.player_code}>
              <td>
                <Link href={`/player/${p.player_code}`}>
                  {p.player_name}
                </Link>
              </td>
              <td>{p.team}</td>
              <td>{p.off_rtg}</td>
              <td>{p.def_rtg}</td>
              <td>{p.adj_rapm_margin}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* PAGINATION */}
      <div style={{ marginTop: 20 }}>
        <button onClick={() => setPage((p) => Math.max(p - 1, 0))}>
          Prev
        </button>
        <button onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>
    </div>
  );
}