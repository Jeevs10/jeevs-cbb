"use client";

import Link from "next/link";
import { Player, SortDirection } from "@/types";
import {
  formatYear,
  formatNumber,
  formatHeight,
  getSortIcon,
  getTableCellClasses,
  getTableHeaderClasses,
  TABLE_CONFIG
} from "@/lib/utils";

interface PlayerTableProps {
  players: Player[];
  sort: string;
  order: SortDirection;
  onSort: (column: string) => void;
  loading?: boolean;
  dataTier?: "basic" | "enriched";
  selectedYear?: string | null;
}

const basicSortableColumns = [
  { key: "Name", label: "Name" },
  { key: "Team", label: "Team" },
  { key: "Season", label: "Season" },
  { key: "Position", label: "Position" },
  { key: "PPG", label: "PPG" },
  { key: "APG", label: "APG" },
  { key: "RPG", label: "RPG" },
  { key: "SPG", label: "SPG" },
  { key: "BPG", label: "BPG" },
  { key: "BPM", label: "BPM" },
  { key: "MPG", label: "MPG" },
];

const enrichedSortableColumns = [
  { key: "year", label: "Year" },
  { key: "roster.height", label: "Height" },
  { key: "off_team_poss_pct", label: "Poss%" },
  { key: "adj_rapm_margin", label: "RAPM" },
  { key: "off_rtg", label: "ORtg" },
  { key: "def_rtg", label: "DRtg" },
  { key: "off_usage", label: "USG" },
  { key: "off_orb", label: "OR%" },
  { key: "def_orb", label: "DR%" },
  { key: "off_assist", label: "AST%" },
  { key: "off_to", label: "TO%" },
  { key: "def_stl", label: "STL%" },
  { key: "def_blk", label: "BLK%" },
  { key: "off_ftr", label: "FTR" },
  { key: "off_threepr", label: "3P%" },
  { key: "BPM", label: "BPM" },
  { key: "VORP", label: "VORP" },
];

export function PlayerTable({ players, sort, order, onSort, loading, dataTier = "enriched", selectedYear }: PlayerTableProps) {
  const handleSort = (column: string) => {
    if (TABLE_CONFIG.SORTABLE_COLUMNS.has(column)) {
      onSort(column);
    }
  };

  const getPlayerHref = (player: Player) => {
    const yearToUse = selectedYear && selectedYear !== "career" ? selectedYear : (player.year ?? "2024");
    return `/player/${player.AthleteSourceId}?year=${yearToUse}`;
  };

  const formatDerivedStat = (value: any): string => {
    if (value === null || value === undefined || isNaN(value)) return "—";
    return value.toFixed(1);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto"></div>
          <p className="mt-2 text-xs">Loading players...</p>
        </div>
      </div>
    );
  }

  if (players.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-xs font-bold text-black uppercase tracking-wide">No players found</h3>
        <p className="mt-2 text-xs text-black">Try adjusting your search or filters</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto border-2 border-black bg-[#C7D0B8] shadow-[3px_3px_0px-black]">
      <table className={`border-collapse text-[10px] sm:text-xs ${dataTier === "basic" ? "min-w-[600px]" : "min-w-[1800px]"}`}>
        <thead>
          <tr>
            {dataTier === "basic" ? (
              // Basic player columns
              basicSortableColumns.map((column) => (
                <th
                  key={column.key}
                  className={getTableHeaderClasses(TABLE_CONFIG.SORTABLE_COLUMNS.has(column.key))}
                  onClick={() => handleSort(column.key)}
                >
                  {column.label}
                  {getSortIcon(sort, column.key, order)}
                </th>
              ))
            ) : (
              // Enriched player columns
              <>
                <th className={getTableHeaderClasses(false)}>
                  Player
                </th>
                <th className={getTableHeaderClasses(false)}>
                  Team
                </th>
                {enrichedSortableColumns.map((column) => (
                  <th
                    key={column.key}
                    className={getTableHeaderClasses(TABLE_CONFIG.SORTABLE_COLUMNS.has(column.key))}
                    onClick={() => handleSort(column.key)}
                  >
                    {column.label}
                    {getSortIcon(sort, column.key, order)}
                  </th>
                ))}
              </>
            )}
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr
              key={`${player.AthleteSourceId}-${player.year ?? index}`}
              className="bg-[#E7E8D1] hover:bg-[#dfe2c6]"
              style={{
                animation: `fadeIn 0.3s ease-out ${index * 0.03}s both`
              }}
            >
              {dataTier === "basic" ? (
                // Basic player row
                <>
                  <td className={getTableCellClasses(true)}>
                    <Link
                      href={getPlayerHref(player)}
                      className="underline hover:no-underline"
                    >
                      {player.Name || player.player_name}
                    </Link>
                  </td>
                  <td className={getTableCellClasses()}>
                    {player.Team || player.team}
                  </td>
                  <td className={getTableCellClasses()}>
                    {player.Season || formatYear(player)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {player.Position || player["roster.pos"] || "-"}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.PPG)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.APG)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.RPG)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.SPG)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.BPG)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.BPM)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.MPG)}
                  </td>
                </>
              ) : (
                // Enriched player row
                <>
                  <td className={getTableCellClasses(true)}>
                    <Link
                      href={getPlayerHref(player)}
                      className="underline hover:no-underline"
                    >
                      {player.player_name}
                    </Link>
                  </td>
                  <td className={getTableCellClasses()}>
                    {player.team}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatYear(player)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatHeight(player["roster.height"])}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_team_poss_pct)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.adj_rapm_margin)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_rtg)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.def_rtg)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_usage)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_orb)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.def_orb)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_assist)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_to)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.def_stl)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.def_blk)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_ftr)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatNumber(player.off_threepr)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.BPM)}
                  </td>
                  <td className={getTableCellClasses()}>
                    {formatDerivedStat(player.VORP)}
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
