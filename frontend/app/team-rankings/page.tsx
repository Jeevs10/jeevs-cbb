"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import Link from "next/link";
import { useYear } from "@/app/context/YearContext";
import { fetchAllTeams, fetchYears } from "@/lib/api";

interface TeamRanking {
  id: string;
  school: string;
  mascot: string | null;
  display_name: string | null;
  conference: string | null;
  wins: number | null;
  losses: number | null;
  adj_net: number | null;
  off_adj_ppp: number | null;
  def_adj_ppp: number | null;
  wab: number | null;
  rank_adj_net?: number | null;
  rank_off_adj_ppp?: number | null;
  rank_def_adj_ppp?: number | null;
  rank_wab?: number | null;
}

type SortDirection = "asc" | "desc";

export default function TeamRankingsPage() {
  const { year, setYear } = useYear();
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [teams, setTeams] = useState<TeamRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState("adj_net");
  const [order, setOrder] = useState<SortDirection>("desc");
  const [conferenceFilter, setConferenceFilter] = useState<string>("all");
  const [availableConferences, setAvailableConferences] = useState<string[]>([]);

  useEffect(() => {
    // Fetch available years first
    fetchYears()
      .then((years: number[]) => {
        console.log("Years fetched:", years);
        setAvailableYears(years);
        // Set default year to the latest available year if not already set
        if (year === null && years.length > 0) {
          setYear(years[years.length - 1]);
        }
      })
      .catch((err: any) => {
        console.error("Error fetching years:", err);
        // Fallback to hardcoded years if API fails
        setAvailableYears([2025, 2026]);
      });
  }, []);

  useEffect(() => {
    fetchAllTeams(year)
      .then((data: any) => {
        const teamsData = (data.results || []).map((team: any) => ({
          id: team.id,
          school: team.school,
          mascot: team.mascot,
          display_name: team.display_name,
          conference: team.conference,
          wins: team.mini_stats?.wins || null,
          losses: team.mini_stats?.losses || null,
          adj_net: team.mini_stats?.adj_net || null,
          off_adj_ppp: team.mini_stats?.off_adj_ppp || null,
          def_adj_ppp: team.mini_stats?.def_adj_ppp || null,
          wab: team.mini_stats?.wab || null,
          rank_adj_net: team.mini_stats?.rank_adj_net || null,
          rank_off_adj_ppp: team.mini_stats?.rank_off_adj_ppp || null,
          rank_def_adj_ppp: team.mini_stats?.rank_def_adj_ppp || null,
          rank_wab: team.mini_stats?.rank_wab || null,
        }));
        
        setTeams(teamsData);
        
        // Extract unique conferences
        const conferences = Array.from(new Set(teamsData.map((t: TeamRanking) => t.conference).filter(Boolean))) as string[];
        setAvailableConferences(conferences.sort());
        
        setLoading(false);
      })
      .catch((err: any) => {
        console.error("Error fetching teams:", err);
        setError("Failed to load team rankings");
        setLoading(false);
      });
  }, [year]);

  // Handle sort changes
  const handleSort = useCallback((column: string) => {
    if (sort === column) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(column);
      setOrder("desc");
    }
  }, [sort]);

  // Filter and sort teams
  const filteredAndSortedTeams = useMemo(() => {
    let filtered = teams;
    
    // Filter by conference
    if (conferenceFilter !== "all") {
      filtered = filtered.filter(team => team.conference === conferenceFilter);
    }
    
    // Sort
    const sorted = [...filtered].sort((a, b) => {
      const aVal = a[sort as keyof TeamRanking] as number | string | null;
      const bVal = b[sort as keyof TeamRanking] as number | string | null;
      
      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return 1;
      if (bVal === null) return -1;
      
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return order === "asc" ? comparison : -comparison;
    });
    
    // Add ranking based on adj_net (official ranking)
    return sorted.map((team, index) => ({
      ...team,
      official_rank: index + 1,
    }));
  }, [teams, conferenceFilter, sort, order]);

  const SortHeader = ({ column, label }: { column: string; label: string }) => (
    <th
      onClick={() => handleSort(column)}
      className="px-4 py-2 text-left cursor-pointer hover:bg-black/5 border-b-2 border-black"
    >
      <div className="flex items-center gap-1">
        {label}
        {sort === column && (
          <span className="text-xs">{order === "asc" ? "↑" : "↓"}</span>
        )}
      </div>
    </th>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING TEAM RANKINGS...
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        {error}
      </div>
    );
  }

  return (
    <div className="p-4 font-mono text-xs">
      <div className="mt-4 space-y-4">
        {/* Year Dropdown */}
        {availableYears.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="font-bold">Season:</span>
            <select
              value={year ?? ""}
              onChange={(e) => {
                const value = e.target.value;
                setYear(value === "" ? null : Number(value));
              }}
              className="bg-white border-2 border-black px-2 py-1 font-mono text-black"
            >
              <option value="">Latest</option>
              {availableYears.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Conference Filter */}
        <div className="flex items-center gap-2">
          <span className="font-bold">Conference:</span>
          <select
            value={conferenceFilter}
            onChange={(e) => setConferenceFilter(e.target.value)}
            className="bg-white border-2 border-black px-2 py-1 font-mono text-black"
          >
            <option value="all">All Conferences</option>
            {availableConferences.map((conf) => (
              <option key={conf} value={conf}>
                {conf}
              </option>
            ))}
          </select>
        </div>

        {/* Count */}
        <div className="text-[10px] opacity-70">
          Showing {filteredAndSortedTeams.length} teams
          {conferenceFilter !== "all" && ` (${conferenceFilter})`}
        </div>

        {/* Table */}
        <div className="border-2 border-black overflow-hidden">
          <table className="w-full">
            <thead className="bg-[#B7C4A5]">
              <tr>
                <th className="px-4 py-2 text-left border-b-2 border-black">Rank</th>
                <SortHeader column="school" label="Team" />
                <SortHeader column="conference" label="Conference" />
                <SortHeader column="wins" label="W-L" />
                <SortHeader column="adj_net" label="ADJ NET" />
                <SortHeader column="off_adj_ppp" label="ADJ Off PPP" />
                <SortHeader column="def_adj_ppp" label="ADJ Def PPP" />
                <SortHeader column="wab" label="WAB" />
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedTeams.map((team) => (
                <tr key={team.id} className="border-b border-black hover:bg-black/5">
                  <td className="px-4 py-2 font-bold text-center">
                    {(team as any).official_rank}
                  </td>
                  <td className="px-4 py-2">
                    <Link
                      href={`/team/${team.id}`}
                      className="font-bold hover:underline"
                    >
                      {team.display_name || team.school}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{team.conference || "—"}</td>
                  <td className="px-4 py-2">
                    {team.wins !== null && team.losses !== null
                      ? `${team.wins}-${team.losses}`
                      : "—"}
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono">
                        {team.adj_net !== null ? team.adj_net.toFixed(1) : "—"}
                      </span>
                      {team.rank_adj_net && (
                        <span className="text-[9px] text-gray-500">
                          #{team.rank_adj_net}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono">
                        {team.off_adj_ppp !== null ? team.off_adj_ppp.toFixed(1) : "—"}
                      </span>
                      {team.rank_off_adj_ppp && (
                        <span className="text-[9px] text-gray-500">
                          #{team.rank_off_adj_ppp}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono">
                        {team.def_adj_ppp !== null ? team.def_adj_ppp.toFixed(1) : "—"}
                      </span>
                      {team.rank_def_adj_ppp && (
                        <span className="text-[9px] text-gray-500">
                          #{team.rank_def_adj_ppp}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono">
                        {team.wab !== null && team.wab !== undefined ? team.wab.toFixed(1) : "—"}
                      </span>
                      {team.rank_wab && team.rank_wab !== null && (
                        <span className="text-[9px] text-gray-500">
                          #{team.rank_wab}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
