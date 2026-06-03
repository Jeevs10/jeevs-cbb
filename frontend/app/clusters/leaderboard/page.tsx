"use client";

import { useState, useCallback, useEffect } from "react";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { PlayerTable } from "@/components/player/PlayerTable";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { YearType, SortDirection } from "@/types";
import { DEFAULT_PAGE_SIZE } from "@/lib/utils";

interface ClusterDescription {
  cluster_id: number;
  name: string;
  count: number;
  avg_height: number;
  avg_usage: number;
  avg_bpm: number;
  top_players: Array<{ Name: string; Team: string; BPM: number }>;
}

interface ClusterRankingsResponse {
  results: any[];
  count: number;
  filtered_count: number;
  cluster_info: ClusterDescription;
  success: boolean;
  error?: string;
}

export default function ClusterLeaderboard() {
  const [clusterId, setClusterId] = useState<number>(0);
  const [year, setYear] = useState<YearType>(null);
  const [sort, setSort] = useState("BPM");
  const [order, setOrder] = useState<SortDirection>("desc");
  const [page, setPage] = useState(0);
  
  const [clusterDescriptions, setClusterDescriptions] = useState<ClusterDescription[]>([]);
  const [players, setPlayers] = useState<any[]>([]);
  const [filteredCount, setFilteredCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch cluster descriptions on mount
  useEffect(() => {
    fetchClusterDescriptions();
  }, []);

  // Fetch cluster descriptions
  const fetchClusterDescriptions = async () => {
    try {
      const response = await fetch("/api/v1/clusters/descriptions");
      if (response.ok) {
        const data = await response.json();
        setClusterDescriptions(data);
      } else {
        setError("Failed to load cluster descriptions");
      }
    } catch (err) {
      setError("Failed to load cluster descriptions");
    }
  };

  // Fetch cluster rankings when filters change
  useEffect(() => {
    if (clusterDescriptions.length > 0) {
      fetchClusterRankings();
    }
  }, [clusterId, year, sort, order, page]);

  const fetchClusterRankings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        cluster_id: clusterId.toString(),
        limit: DEFAULT_PAGE_SIZE.toString(),
        offset: (page * DEFAULT_PAGE_SIZE).toString(),
        sort_by: sort,
        sort_order: order,
      });
      
      if (year) {
        params.append("year", year.toString());
      }
      
      const response = await fetch(`/api/v1/clusters/rankings?${params}`);
      const data: ClusterRankingsResponse = await response.json();
      
      if (data.success) {
        setPlayers(data.results);
        setFilteredCount(data.filtered_count);
      } else {
        setError(data.error || "Failed to load cluster rankings");
      }
    } catch (err) {
      setError("Failed to load cluster rankings");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = useCallback((column: string) => {
    if (sort === column) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(column);
      setOrder("desc");
    }
    setPage(0);
  }, [sort]);

  const handleClusterChange = (newClusterId: number) => {
    setClusterId(newClusterId);
    setPage(0);
  };

  const handleYearChange = (newYear: YearType) => {
    setYear(newYear);
    setPage(0);
  };

  const handlePrevPage = useCallback(() => {
    setPage((p) => Math.max(p - 1, 0));
  }, []);

  const handleNextPage = useCallback(() => {
    setPage((p) => p + 1);
  }, []);

  const handleRetry = useCallback(() => {
    fetchClusterDescriptions();
  }, []);

  const clusterInfo = clusterDescriptions.find(c => c.cluster_id === clusterId);

  return (
    <ErrorBoundary>
      <div className="p-4 font-mono text-xs">
        <h1 className="text-sm font-bold text-black mb-4 uppercase tracking-wide">
          Cluster Leaderboard
        </h1>

        {/* CLUSTER SELECTOR */}
        <div className="mb-4">
          <label className="block text-[10px] font-bold text-black mb-1 uppercase">
            Select Cluster
          </label>
          <select
            value={clusterId}
            onChange={(e) => handleClusterChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border-2 border-black bg-[#E7E8D1] text-xs"
            disabled={loading}
          >
            {clusterDescriptions.map((cluster) => (
              <option key={cluster.cluster_id} value={cluster.cluster_id}>
                {cluster.name} ({cluster.count} players)
              </option>
            ))}
          </select>
        </div>

        {/* YEAR SELECTOR */}
        <div className="mb-4">
          <label className="block text-[10px] font-bold text-black mb-1 uppercase">
            Year
          </label>
          <select
            value={year || ""}
            onChange={(e) => handleYearChange(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-3 py-2 border-2 border-black bg-[#E7E8D1] text-xs"
            disabled={loading}
          >
            <option value="">Latest Year</option>
            <option value="2026">2026</option>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
            <option value="2019">2019</option>
          </select>
        </div>

        {/* CLUSTER INFO */}
        {clusterInfo && (
          <div className="mb-4 p-3 border-2 border-black bg-[#C7D0B8]">
            <h2 className="text-xs font-bold text-black mb-2 uppercase">
              {clusterInfo.name}
            </h2>
            <div className="grid grid-cols-2 gap-2 text-[10px]">
              <div>
                <span className="opacity-70">Total Players:</span> {clusterInfo.count}
              </div>
              <div>
                <span className="opacity-70">Avg Height:</span> {clusterInfo.avg_height.toFixed(1)}"
              </div>
              <div>
                <span className="opacity-70">Avg Usage:</span> {clusterInfo.avg_usage.toFixed(1)}%
              </div>
              <div>
                <span className="opacity-70">Avg BPM:</span> {clusterInfo.avg_bpm.toFixed(2)}
              </div>
            </div>
            <div className="mt-2 text-[10px]">
              <span className="opacity-70">Top Players:</span>
              <ul className="list-disc list-inside mt-1">
                {clusterInfo.top_players.slice(0, 3).map((player, idx) => (
                  <li key={idx}>{player.Name} ({player.Team}): {player.BPM.toFixed(2)}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* COUNT */}
        <div className="mb-2 text-[10px] opacity-70">
          Showing {players.length} players
          {filteredCount > 0 && ` (of ${filteredCount} in cluster)`}
        </div>

        {/* TABLE */}
        {error ? (
          <ErrorMessage 
            message={error} 
            onRetry={handleRetry}
          />
        ) : (
          <PlayerTable
            players={players}
            sort={sort}
            order={order}
            onSort={handleSort}
            loading={loading}
            dataTier="enriched"
          />
        )}

        {/* PAGINATION */}
        {players.length > 0 && (
          <div className="mt-4 flex gap-2">
            <button
              onClick={handlePrevPage}
              disabled={page === 0}
              className="px-4 py-2 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Prev
            </button>
            <button
              onClick={handleNextPage}
              disabled={players.length < DEFAULT_PAGE_SIZE}
              className="px-4 py-2 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
