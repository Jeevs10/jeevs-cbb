"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAllPlayers } from "@/lib/api";

const BASE_URL = "http://localhost:8000";

export default function Home() {
  const [players, setPlayers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const limit = 50;

  // Simple data loading
  useEffect(() => {
    async function loadPlayers() {
      try {
        setLoading(true);
        setError(null);
        console.log("🔍 Fetching players from:", `${BASE_URL}/players`);
        
        const data = await fetchAllPlayers({ limit });
        
        console.log("📊 Received data:", data);
        setPlayers(data);
        setLoading(false);
      } catch (err) {
        console.error("❌ Error loading players:", err);
        setError(err instanceof Error ? err.message : "Failed to load players");
        setLoading(false);
      }
    }

    loadPlayers();
  }, []);

  return (
    <div className="p-4 font-mono text-xs">
      <h1 className="text-xl font-bold mb-3">Player Leaderboard</h1>
      
      {/* DEBUG INFO */}
      <div className="mb-3 p-3 bg-yellow-100 border border-yellow-300 rounded">
        <h2 className="font-bold mb-2">Debug Information</h2>
        <p><strong>Loading:</strong> {loading ? "Yes" : "No"}</p>
        <p><strong>Players Count:</strong> {players.length}</p>
        <p><strong>Error:</strong> {error || "None"}</p>
        <p><strong>API URL:</strong> {BASE_URL}/players</p>
      </div>

      {/* PLAYER TABLE */}
      {loading ? (
        <div className="text-center py-8">Loading players...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">Error: {error}</div>
      ) : (
        <div className="overflow-x-auto border-4 border-black bg-[#C7D0B8] shadow-[6px_6px_0px_black]">
          <table className="min-w-[1800px] border-collapse">
            <thead>
              <tr>
                <th className="p-2 border border-black sticky left-0 z-30">Player</th>
                <th className="p-2 border border-black">Team</th>
                <th className="p-2 border border-black">Year</th>
                <th className="p-2 border border-black">RAPM</th>
              </tr>
            </thead>
            <tbody>
              {players.map((p, i) => (
                <tr key={`${p.player_code}-${p.year ?? i}`} className="bg-[#E7E8D1] hover:bg-[#dfe2c6]">
                  <td className="p-2 border border-black sticky left-0 bg-[#E7E8D1] z-20 whitespace-nowrap">
                    <Link href={`/player/${p.player_code}`} className="underline">
                      {p.player_name}
                    </Link>
                  </td>
                  <td className="p-2 border border-black">{p.team}</td>
                  <td className="p-2 border border-black">{p.year}</td>
                  <td className="p-2 border border-black">{p.adj_rapm_margin}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
