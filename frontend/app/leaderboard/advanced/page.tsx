"use client";

import { useState, useCallback, useMemo } from "react";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { PlayerTable } from "@/components/player/PlayerTable";
import { PlayerSearch } from "@/components/player/PlayerSearch";
import { YearFilter } from "@/components/player/YearFilter";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { usePlayers } from "@/hooks/usePlayers";
import { useYears } from "@/hooks/useYears";
import { YearType, SortDirection } from "@/types";
import { DEFAULT_PAGE_SIZE } from "@/lib/utils";

export default function AdvancedLeaderboard() {
  const [sort, setSort] = useState("adj_rapm_margin");
  const [order, setOrder] = useState<SortDirection>("desc");
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [year, setYear] = useState<YearType>(null);

  // Fetch years data
  const { years, loading: yearsLoading, error: yearsError } = useYears();

  // Memoize years array to ensure stable reference
  const memoizedYears = useMemo(() => years, [years]);

  // Fetch only enriched players with advanced metrics
  const { 
    players, 
    loading: playersLoading, 
    error: playersError,
    filteredCount 
  } = usePlayers({
    limit: DEFAULT_PAGE_SIZE,
    offset: page * DEFAULT_PAGE_SIZE,
    sort,
    order,
    year: year === "career" ? "career" : (year ?? undefined),
    search: search || undefined,
    dataTier: "enriched", // Only fetch enriched players
  });

  // Handle sort changes
  const handleSort = useCallback((column: string) => {
    if (sort === column) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(column);
      setOrder("desc");
    }
    setPage(0);
  }, [sort]);

  // Handle year changes
  const handleYearChange = useCallback((newYear: YearType) => {
    setYear(newYear);
    setPage(0);
  }, []);

  // Handle search changes
  const handleSearchChange = useCallback((newSearch: string) => {
    setSearch(newSearch);
    setPage(0);
  }, []);

  // Handle pagination
  const handlePrevPage = useCallback(() => {
    setPage((p) => Math.max(p - 1, 0));
  }, []);

  const handleNextPage = useCallback(() => {
    setPage((p) => p + 1);
  }, []);

  // Handle error retries
  const handleRetryYears = useCallback(() => {
    window.location.reload();
  }, []);

  const handleRetryPlayers = useCallback(() => {
    window.location.reload();
  }, []);

  return (
    <ErrorBoundary>
      <div className="p-4 font-mono text-xs">

        {/* YEAR FILTER */}
        {yearsError ? (
          <ErrorMessage 
            message={yearsError} 
            onRetry={handleRetryYears}
          />
        ) : (
          <YearFilter
            years={memoizedYears}
            selectedYear={year}
            onYearChange={handleYearChange}
            loading={yearsLoading}
          />
        )}

        {/* SEARCH */}
        <PlayerSearch
          value={search}
          onChange={handleSearchChange}
          onEnter={() => setPage(0)}
          disabled={playersLoading}
        />

        {/* COUNT */}
        <div className="mb-2 text-[10px] opacity-70">
          Showing {players.length} advanced players
          {filteredCount > 0 && ` (of ${filteredCount} filtered)`}
        </div>

        {/* TABLE */}
        {playersError ? (
          <ErrorMessage 
            message={playersError} 
            onRetry={handleRetryPlayers}
          />
        ) : (
          <PlayerTable
            players={players}
            sort={sort}
            order={order}
            onSort={handleSort}
            loading={playersLoading}
            dataTier="enriched"
            selectedYear={year === null ? null : (year === "career" ? "career" : String(year))}
          />
        )}

        {/* PAGINATION */}
        {!search.trim() && players.length > 0 && (
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
