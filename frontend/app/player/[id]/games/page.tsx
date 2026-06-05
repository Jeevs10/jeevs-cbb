"use client";

import { useEffect, useState } from "react";
import { fetchPlayerGames, fetchPlayer } from "@/lib/api";
import { useParams, useSearchParams, useRouter } from "next/navigation";

interface GameData {
  numdate: string;
  datetext: string;
  opponent: string;
  loc: string;
  pts: number;
  Min_per: number;
  ORtg: number;
  Usage: number;
  eFG: number;
  ORB: number;
  DRB: number;
  AST: number;
  TOV: number;
  STL: number;
  BLK: number;
  PF: number;
  bpm: number;
  win2: number;
  twoPM: number;
  twoPA: number;
  TPM: number;
  TPA: number;
  FTM: number;
  FTA: number;
  dunksmade: number;
  dunksatt: number;
  rimmade: number;
  rimatt: number;
  midmade: number;
  midatt: number;
  AST_per: number;
  stl_per: number;
  blk_per: number;
  ORB_per: number;
  DRB_per: number;
  TO_per: number;
  TS_per: number;
  bpm_rd: number;
  bpm_net: number;
  sbpm: number;
  possessions: number;
}

type StatField = keyof GameData;

interface StatOption {
  key: StatField;
  label: string;
  formatter: (value: any, game: GameData) => string;
}

const statOptions: StatOption[] = [
  { key: "Min_per", label: "MIN", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "pts", label: "PTS", formatter: (v) => v || 0 },
  { key: "ORB", label: "ORB", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "DRB", label: "DRB", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "AST", label: "AST", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "TOV", label: "TOV", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "STL", label: "STL", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "BLK", label: "BLK", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "PF", label: "PF", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "bpm", label: "BPM", formatter: (v) => (v >= 0 ? "+" : "") + (v?.toFixed(1) || "-") },
  { key: "twoPM", label: "2PM", formatter: (v) => v || 0 },
  { key: "twoPA", label: "2PA", formatter: (v) => v || 0 },
  { key: "TPM", label: "3PM", formatter: (v) => v || 0 },
  { key: "TPA", label: "3PA", formatter: (v) => v || 0 },
  { key: "FTM", label: "FTM", formatter: (v) => v || 0 },
  { key: "FTA", label: "FTA", formatter: (v) => v || 0 },
  { key: "dunksmade", label: "Dunks", formatter: (v) => v || 0 },
  { key: "dunksatt", label: "Dunk Att", formatter: (v) => v || 0 },
  { key: "rimmade", label: "Rim Made", formatter: (v) => v || 0 },
  { key: "rimatt", label: "Rim Att", formatter: (v) => v || 0 },
  { key: "midmade", label: "Mid Made", formatter: (v) => v || 0 },
  { key: "midatt", label: "Mid Att", formatter: (v) => v || 0 },
  { key: "AST_per", label: "AST%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "stl_per", label: "STL%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "blk_per", label: "BLK%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "ORB_per", label: "ORB%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "DRB_per", label: "DRB%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "TO_per", label: "TO%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "ORtg", label: "ORtg", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "Usage", label: "Usage%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "eFG", label: "eFG%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "TS_per", label: "TS%", formatter: (v) => v?.toFixed(1) + "%" || "-" },
  { key: "bpm_rd", label: "BPM-RD", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "bpm_net", label: "BPM-Net", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "sbpm", label: "SBPM", formatter: (v) => v?.toFixed(1) || "-" },
  { key: "possessions", label: "Poss", formatter: (v) => v?.toFixed(0) || "-" },
];

const defaultSelectedStats: StatField[] = [
  "Min_per", "pts", "ORB", "DRB", "AST", "TOV", "STL", "BLK", "PF", "bpm"
];

export default function PlayerGameLogPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const playerId = params.id as string;
  const [games, setGames] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStats, setSelectedStats] = useState<StatField[]>(defaultSelectedStats);
  const [showStatSelector, setShowStatSelector] = useState(false);
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  // Get year from URL params, default to 2026
  useEffect(() => {
    const yearParam = searchParams.get('year');
    if (yearParam) {
      setSelectedYear(parseInt(yearParam));
    }
  }, [searchParams]);

  // Fetch player data to get available years
  useEffect(() => {
    if (!playerId) return;

    fetchPlayer(playerId, selectedYear)
      .then((data) => {
        setAvailableYears(data.available_years || []);
        // If the current selected year is not in available years, switch to the first available year
        if (data.available_years && data.available_years.length > 0) {
          if (!data.available_years.includes(selectedYear)) {
            setSelectedYear(data.available_years[0]);
            router.push(`/player/${playerId}/games?year=${data.available_years[0]}`);
          }
        }
      })
      .catch(() => {});
  }, [playerId]);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const data = await fetchPlayerGames(playerId, selectedYear, 1000);
        setGames(data.games || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load games");
      } finally {
        setLoading(false);
      }
    };

    if (playerId) {
      fetchGames();
    }
  }, [playerId, selectedYear]);

  const handleYearChange = (year: number) => {
    setSelectedYear(year);
    router.push(`/player/${playerId}/games?year=${year}`);
  };

  const toggleStat = (statKey: StatField) => {
    setSelectedStats(prev =>
      prev.includes(statKey)
        ? prev.filter(s => s !== statKey)
        : [...prev, statKey]
    );
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center text-black">Loading game log...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-center text-black">{error}</div>
      </div>
    );
  }

  const selectedStatOptions = statOptions.filter(opt => selectedStats.includes(opt.key));

  return (
    <div className="p-2 sm:p-6">
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xs sm:text-sm font-bold mb-2 uppercase tracking-wide">GAME LOG</h1>
        <div className="flex gap-2 sm:gap-4 items-center flex-wrap">
          <div className="flex gap-2">
            {availableYears.map(year => (
              <button
                key={year}
                onClick={() => handleYearChange(year)}
                className={`px-2 py-1 sm:px-4 sm:py-2 border-2 border-black font-bold text-[10px] sm:text-xs transition-colors shadow-[3px_3px_0px-black] ${
                  selectedYear === year
                    ? "bg-[#E7E8D1] text-black"
                    : "bg-[#E7E8D1] text-black hover:bg-[#B8C0A8]"
                }`}
              >
                {year}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowStatSelector(!showStatSelector)}
            className="px-2 py-1 sm:px-4 sm:py-2 border-2 border-black bg-[#E7E8D1] text-black font-bold text-[10px] sm:text-xs hover:bg-[#B8C0A8] transition-colors shadow-[3px_3px_0px-black]"
          >
            {showStatSelector ? "HIDE STATS" : "SELECT STATS"}
          </button>
          <span className="text-[10px] sm:text-xs text-black">
            {games.length} games
          </span>
        </div>
      </div>

      {showStatSelector && (
        <div className="mb-4 sm:mb-6 p-2 sm:p-4 border-2 border-black bg-[#E7E8D1] shadow-[3px_3px_0px-black]">
          <h3 className="font-bold mb-2 sm:mb-3 uppercase tracking-wide text-[10px] sm:text-xs">SELECT STATISTICS TO DISPLAY</h3>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
            {statOptions.map(option => (
              <label key={option.key} className="flex items-center gap-2 text-[10px] sm:text-xs cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedStats.includes(option.key)}
                  onChange={() => toggleStat(option.key)}
                  className="border-2 border-black"
                />
                {option.label}
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-[10px] sm:text-xs font-mono border-collapse border-2 border-black min-w-[600px]">
          <thead>
            <tr className="border-b-2 border-black bg-[#B8C0A8]">
              <th className="text-left p-1 sm:p-2 font-bold text-[10px] sm:text-xs">DATE</th>
              <th className="text-left p-1 sm:p-2 font-bold text-[10px] sm:text-xs">OPP</th>
              <th className="text-center p-1 sm:p-2 font-bold text-[10px] sm:text-xs">RESULT</th>
              {selectedStatOptions.map(option => (
                <th key={option.key} className="text-center p-1 sm:p-2 font-bold text-[10px] sm:text-xs">
                  {option.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {games.map((game, index) => (
              <tr
                key={`${game.numdate}-${index}`}
                className={`border-b-2 border-black hover:bg-[#B8C0A8] ${
                  game.win2 === 1 ? "bg-[#C7D0B8]" : "bg-[#E7E8D1]"
                }`}
              >
                <td className="p-1 sm:p-2">
                  <div className="font-bold text-[10px] sm:text-xs">{game.datetext}</div>
                  <div className="text-[10px] sm:text-xs text-black">
                    {game.loc === "H" ? "vs" : game.loc === "A" ? "@" : "N"}
                  </div>
                </td>
                <td className="p-1 sm:p-2 font-bold text-[10px] sm:text-xs">{game.opponent}</td>
                <td className="text-center p-1 sm:p-2 font-bold text-[10px] sm:text-xs">
                  {game.win2 === 1 ? "W" : "L"}
                </td>
                {selectedStatOptions.map(option => (
                  <td key={option.key} className="text-center p-1 sm:p-2 text-[10px] sm:text-xs">
                    {option.formatter(game[option.key], game)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
