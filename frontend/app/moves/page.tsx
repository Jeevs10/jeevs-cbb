"use client";

import { useState, useCallback, useMemo } from "react";
import Link from "next/link";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { YearFilter } from "@/components/player/YearFilter";
import { PlayerSearch } from "@/components/player/PlayerSearch";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { useYears } from "@/hooks/useYears";
import { useMovesRankings } from "@/hooks/useMovesRankings";
import { YearType } from "@/types";
import { DEFAULT_PAGE_SIZE } from "@/lib/utils";

const MOVE_TYPES = [
  { value: "rim_attack", label: "Rim Attack", color: "bg-[#FFB3BA]" },
  { value: "sniper", label: "Sniper", color: "bg-[#B5EAD7]" },
  { value: "mid_range", label: "Mid-Range Assassin", color: "bg-[#E2D1F9]" },
  { value: "transition", label: "Transition Bolt", color: "bg-[#C1E1C1]" },
  { value: "pnr_maestro", label: "PnR Maestro", color: "bg-[#AECBFA]" },
  { value: "post_dominator", label: "Post Dominator", color: "bg-[#FFDAB9]" },
];

const POSITIONS = [
  { value: "all", label: "All Positions" },
  { value: "PG", label: "PG" },
  { value: "SG", label: "SG" },
  { value: "SF", label: "SF" },
  { value: "PF", label: "PF" },
  { value: "C", label: "C" },
];

const CONFERENCES = [
  { value: "all", label: "All Conferences" },
  { value: "ACC", label: "ACC" },
  { value: "Big 12", label: "Big 12" },
  { value: "Big East", label: "Big East" },
  { value: "Big Ten", label: "Big Ten" },
  { value: "SEC", label: "SEC" },
  { value: "Pac-12", label: "Pac-12" },
  { value: "Big West", label: "Big West" },
  { value: "Mountain West", label: "Mountain West" },
  { value: "West Coast", label: "West Coast" },
  { value: "Atlantic 10", label: "Atlantic 10" },
  { value: "American", label: "American" },
  { value: "Conference USA", label: "Conference USA" },
  { value: "Mid-American", label: "Mid-American" },
  { value: "Missouri Valley", label: "Missouri Valley" },
];

export default function MovesPage() {
  const [move, setMove] = useState("rim_attack");
  const [year, setYear] = useState<YearType>(null);
  const [position, setPosition] = useState<string>("all");
  const [conference, setConference] = useState<string>("all");
  const [highMajor, setHighMajor] = useState<boolean>(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState<string>("grade_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Fetch years data
  const { years, loading: yearsLoading, error: yearsError } = useYears();

  // Memoize years array to ensure stable reference
  const memoizedYears = useMemo(() => years, [years]);

  // Fetch moves rankings
  const { data: rankings, loading: rankingsLoading, error: rankingsError } = useMovesRankings({
    moveType: move,
    year: year ? String(year) : undefined,
    limit: DEFAULT_PAGE_SIZE,
    offset: page * DEFAULT_PAGE_SIZE,
    position: position === "all" ? undefined : position,
    conference: conference === "all" ? undefined : conference,
    highMajor: highMajor || undefined,
    search: search || undefined,
    sortBy,
    sortOrder,
  });

  // Handle year changes
  const handleYearChange = useCallback((newYear: YearType) => {
    setYear(newYear);
  }, []);

  // Handle move changes
  const handleMoveChange = useCallback((newMove: string) => {
    setMove(newMove);
    setPage(0);
  }, []);

  // Handle position changes
  const handlePositionChange = useCallback((newPosition: string) => {
    setPosition(newPosition);
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

  // Handle sort changes
  const handleSort = useCallback((field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "desc" ? "asc" : "desc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
    setPage(0);
  }, [sortBy, sortOrder]);

  // Handle error retries
  const handleRetryYears = useCallback(() => {
    window.location.reload();
  }, []);

  const handleRetryRankings = useCallback(() => {
    window.location.reload();
  }, []);

  return (
    <ErrorBoundary>
      <div className="p-2 sm:p-4 font-mono text-xs">

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

        {/* MOVE FILTER */}
        <div className="mb-6">
          <label className="block text-xs font-bold mb-3 text-black uppercase tracking-wide">MOVE TYPE</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {MOVE_TYPES.map((moveType) => (
              <button
                key={moveType.value}
                onClick={() => handleMoveChange(moveType.value)}
                className={`px-3 py-2 sm:px-4 sm:py-3 border-2 border-black text-[10px] sm:text-xs font-bold transition-all ${
                  move === moveType.value
                    ? `${moveType.color} shadow-[3px_3px_0px_black]`
                    : 'bg-[#E7E8D1] hover:bg-[#B8C0A8] shadow-[3px_3px_0px_black]'
                }`}
              >
                {moveType.label}
              </button>
            ))}
          </div>
        </div>

        {/* POSITION FILTER */}
        <div className="mb-4">
          <label className="block text-xs font-bold mb-1 uppercase tracking-wide">POSITION</label>
          <select
            value={position}
            onChange={(e) => handlePositionChange(e.target.value)}
            className="w-full px-2 py-1 border-2 border-black bg-[#E7E8D1] text-xs shadow-[3px_3px_0px_black]"
          >
            {POSITIONS.map((pos) => (
              <option key={pos.value} value={pos.value}>
                {pos.label}
              </option>
            ))}
          </select>
        </div>

        {/* CONFERENCE FILTER */}
        <div className="mb-4">
          <label className="block text-xs font-bold mb-1 uppercase tracking-wide">CONFERENCE</label>
          <select
            value={conference}
            onChange={(e) => {
              setConference(e.target.value);
              setPage(0);
            }}
            className="w-full px-2 py-1 border-2 border-black bg-[#E7E8D1] text-xs shadow-[3px_3px_0px_black]"
          >
            {CONFERENCES.map((conf) => (
              <option key={conf.value} value={conf.value}>
                {conf.label}
              </option>
            ))}
          </select>
        </div>

        {/* HIGH MAJOR FILTER */}
        <div className="mb-4 flex items-center gap-2">
          <input
            type="checkbox"
            id="highMajor"
            checked={highMajor}
            onChange={(e) => {
              setHighMajor(e.target.checked);
              setPage(0);
            }}
            className="w-4 h-4 border-2 border-black"
          />
          <label htmlFor="highMajor" className="text-xs font-bold uppercase tracking-wide">HIGH MAJOR ONLY</label>
        </div>

        {/* SEARCH */}
        <PlayerSearch
          value={search}
          onChange={handleSearchChange}
          disabled={rankingsLoading}
          placeholder="Search players or teams..."
        />

        {/* COUNT */}
        <div className="mb-2 text-xs text-black">
          Showing {rankings?.results.length || 0} players
          {rankings?.filtered_count && rankings.filtered_count > 0 && ` (of ${rankings.filtered_count} filtered)`}
        </div>

        {/* MOVE RANKINGS */}
        <div key={`rankings-${move}`} className="border-2 border-black bg-[#C7D0B8] p-2 sm:p-3 shadow-[3px_3px_0px-black] overflow-x-auto">
          <div className="text-xs font-bold border-b-2 border-black pb-1 mb-2 uppercase tracking-wide">
            {MOVE_TYPES.find(m => m.value === move)?.label} RANKINGS
          </div>

          {rankingsError ? (
            <ErrorMessage
              message={rankingsError}
              onRetry={handleRetryRankings}
            />
          ) : rankings && rankings.results.length > 0 ? (
            <div className="space-y-1 min-w-[600px]">
              {/* Table Header */}
              <div className={`grid gap-2 text-[10px] sm:text-xs font-bold border-b-2 border-black pb-1 ${year ? "grid-cols-9" : "grid-cols-10"}`}>
                <div>PLAYER</div>
                <div>TEAM</div>
                <div>POS</div>
                <div>HT</div>
                {!year && <div>YEAR</div>}
                <div
                  className="text-right cursor-pointer hover:underline"
                  onClick={() => handleSort("move_frequency_pctile")}
                >
                  FREQ {sortBy === "move_frequency_pctile" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
                </div>
                <div
                  className="text-right cursor-pointer hover:underline"
                  onClick={() => handleSort("move_efficiency")}
                >
                  PPP {sortBy === "move_efficiency" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
                </div>
                <div className="text-right">PPP %</div>
                <div className="text-right">GRADE</div>
                <div
                  className="text-right cursor-pointer hover:underline"
                  onClick={() => handleSort("grade_score")}
                >
                  SCORE {sortBy === "grade_score" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
                </div>
              </div>

              {/* Table Rows */}
              {rankings.results.map((player, index) => {
                const playerId = (player.AthleteSourceId || player['roster.ncaa_id'])?.toString().replace('.0', '');
                return (
                  <Link
                    key={`${move}-${playerId || index}`}
                    href={`/player/${playerId}?year=${player.year}`}
                    className={`grid gap-2 items-center border-2 border-black p-2 bg-[#E7E8D1] hover:bg-[#B8C0A8] transition-colors ${year ? "grid-cols-9" : "grid-cols-10"}`}
                  >
                    <div className="font-bold text-[10px] sm:text-xs">{player.rank || index + 1}. {player.player_name}</div>
                    <div className="text-[10px] sm:text-xs text-black">{player.team}</div>
                    <div className="text-[10px] sm:text-xs text-black">{player.Position || '-'}</div>
                    <div className="text-[10px] sm:text-xs text-black">{player.Height || '-'}</div>
                    {!year && <div className="text-[10px] sm:text-xs text-black">{player.year}</div>}
                    <div className="text-right text-[10px] sm:text-xs">
                      {(player.move_frequency_pctile * 100).toFixed(0)}th %
                    </div>
                    <div className="text-right font-bold text-[10px] sm:text-xs">
                      {player.move_efficiency?.toFixed(2)}
                    </div>
                    <div className="text-right text-[10px] sm:text-xs">
                      {(player.move_efficiency_pctile * 100).toFixed(0)}th %
                    </div>
                    <div className="text-right font-bold text-[10px] sm:text-xs">
                      {player.grade}
                    </div>
                    <div className="text-right text-[10px] sm:text-xs">
                      {player.grade_score?.toFixed(3)}
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="text-xs text-black">No rankings available</div>
          )}

          {/* PAGINATION */}
          {!search.trim() && rankings && rankings.results.length > 0 && (
            <div className="mt-4 flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={page === 0}
                className="px-3 py-2 sm:px-4 sm:py-2 border-2 border-black bg-[#E7E8D1] hover:bg-[#B8C0A8] disabled:opacity-50 disabled:cursor-not-allowed text-xs shadow-[3px_3px_0px-black]"
              >
                Prev
              </button>
              <button
                onClick={handleNextPage}
                disabled={rankings.results.length < DEFAULT_PAGE_SIZE}
                className="px-3 py-2 sm:px-4 sm:py-2 border-2 border-black bg-[#E7E8D1] hover:bg-[#B8C0A8] disabled:opacity-50 disabled:cursor-not-allowed text-xs shadow-[3px_3px_0px-black]"
              >
                Next
              </button>
            </div>
          )}
        </div>

      </div>
    </ErrorBoundary>
  );
}
