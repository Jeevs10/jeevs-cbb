"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LeaderboardEntry {
  player_key: string;
  player_name: string;
  team: string;
  current_bpm: number | null;
  bpm_change_predicted: number | null;
  projected_bpm: number | null;
  projected_bpm_lower_90: number | null;
  projected_bpm_upper_90: number | null;
  ncaa_id: string | null;
}

interface LeaderboardResponse {
  success: boolean;
  count: number;
  total_count: number;
  offset: number;
  limit: number;
  sort_by: string;
  order: string;
  results: LeaderboardEntry[];
}

export default function ProjectionsLeaderboard() {
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState("projected_bpm");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);
  const limit = 50;

  const fetchLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `${BASE_URL}/api/v1/projections/leaderboard?sort_by=${sort}&order=${order}&limit=${limit}&offset=${page * limit}`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch leaderboard data");
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }, [sort, order, page, limit]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const handleSort = (column: string) => {
    if (sort === column) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(column);
      setOrder("desc");
    }
    setPage(0);
  };

  const getSortIcon = (column: string) => {
    if (sort !== column) return "";
    return order === "asc" ? " ↑" : " ↓";
  };

  return (
    <div className="p-2 sm:p-4 font-mono text-xs">
      {/* HEADER */}
      <div className="mb-2 sm:mb-4">
        <h1 className="text-xs sm:text-sm font-bold uppercase tracking-wide">2027 BPM Projection Leaderboard</h1>
      </div>

      {/* COUNT */}
      <div className="mb-2 text-[10px] sm:text-xs opacity-70">
        Showing {data?.results.length || 0} players (of {data?.total_count || 0} total)
      </div>

      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto"></div>
            <p className="mt-2 text-[10px] sm:text-xs">Loading leaderboard...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <h3 className="text-[10px] sm:text-xs font-bold text-black uppercase tracking-wide">Error</h3>
          <p className="mt-2 text-[10px] sm:text-xs text-black">{error}</p>
        </div>
      )}

      {data && !loading && !error && (
        <div className="overflow-x-auto border-2 border-black bg-[#C7D0B8] shadow-[3px_3px_0px_black]">
          <table className="border-collapse min-w-[600px]">
            <thead>
              <tr className="border-b-2 border-black">
                <th
                  className="text-left py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("projected_bpm")}
                >
                  Rank{getSortIcon("projected_bpm")}
                </th>
                <th
                  className="text-left py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("player_name")}
                >
                  Player{getSortIcon("player_name")}
                </th>
                <th
                  className="text-left py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("team")}
                >
                  Team{getSortIcon("team")}
                </th>
                <th
                  className="text-right py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("current_bpm")}
                >
                  Current BPM{getSortIcon("current_bpm")}
                </th>
                <th
                  className="text-right py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("bpm_change")}
                >
                  Projected Change{getSortIcon("bpm_change")}
                </th>
                <th
                  className="text-right py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs cursor-pointer hover:bg-[#B7C4A5] transition-colors"
                  onClick={() => handleSort("projected_bpm")}
                >
                  2027 Projected BPM{getSortIcon("projected_bpm")}
                </th>
                <th className="text-right py-2 px-2 sm:px-3 font-bold text-[10px] sm:text-xs">80% CI</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((entry, index) => (
                <tr
                  key={entry.player_key}
                  className="border-b-2 border-black hover:bg-[#B8C0A8] transition-colors cursor-pointer"
                >
                  <td className="py-2 px-2 sm:px-3 text-[10px] sm:text-xs font-medium">
                    {page * limit + index + 1}
                  </td>
                  <td className="py-2 px-2 sm:px-3 text-[10px] sm:text-xs font-medium">
                    <Link
                      href={`/projections/2027?player=${entry.player_key}`}
                      className="hover:underline"
                    >
                      {entry.player_name}
                    </Link>
                  </td>
                  <td className="py-2 px-2 sm:px-3 text-[10px] sm:text-xs">{entry.team}</td>
                  <td className="py-2 px-2 sm:px-3 text-right text-[10px] sm:text-xs">
                    {entry.current_bpm !== null ? entry.current_bpm.toFixed(2) : "N/A"}
                  </td>
                  <td className="py-2 px-2 sm:px-3 text-right text-[10px] sm:text-xs">
                    {entry.bpm_change_predicted !== null ? (
                      <span
                        className={
                          entry.bpm_change_predicted > 0
                            ? "text-green-700"
                            : entry.bpm_change_predicted < 0
                            ? "text-red-700"
                            : ""
                        }
                      >
                        {entry.bpm_change_predicted > 0 ? "+" : ""}
                        {entry.bpm_change_predicted.toFixed(2)}
                        {entry.bpm_change_predicted > 0 ? " ↑" : entry.bpm_change_predicted < 0 ? " ↓" : ""}
                      </span>
                    ) : (
                      "N/A"
                    )}
                  </td>
                  <td className="py-2 px-2 sm:px-3 text-right text-[10px] sm:text-xs font-bold">
                    {entry.projected_bpm !== null ? entry.projected_bpm.toFixed(2) : "N/A"}
                  </td>
                  <td className="py-2 px-2 sm:px-3 text-right text-[10px] sm:text-xs text-black">
                    {entry.projected_bpm_lower_90 !== null && entry.projected_bpm_upper_90 !== null
                      ? `${entry.projected_bpm_lower_90.toFixed(1)} to ${entry.projected_bpm_upper_90.toFixed(1)}`
                      : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-2 sm:px-4 sm:py-2 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-[10px] sm:text-xs"
            >
              Prev
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= data.total_count}
              className="px-3 py-2 sm:px-4 sm:py-2 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-[10px] sm:text-xs"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
