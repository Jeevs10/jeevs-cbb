"use client";

import { useEffect, useState } from "react";
import { fetchPlayerGames } from "@/lib/api";
import Link from "next/link";

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
}

interface PlayerLatestGamesPanelProps {
  playerId: string;
  year?: number | "career";
}

export default function PlayerLatestGamesPanel({
  playerId,
  year,
}: PlayerLatestGamesPanelProps) {
  const [games, setGames] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handle career mode - use latest year (2026)
  const yearToUse = year === "career" ? 2026 : (year || 2026);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const data = await fetchPlayerGames(playerId, yearToUse, 5);
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
  }, [playerId, yearToUse]);

  if (loading) {
    return (
      <div className="text-center text-xs text-gray-600 py-4">
        Loading recent games...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-xs text-red-600 py-4">
        {error}
      </div>
    );
  }

  if (games.length === 0) {
    return (
      <div className="text-center text-xs text-gray-600 py-4">
        No game data available
      </div>
    );
  }

  const calculateFG = (twoPM: number, twoPA: number, TPM: number, TPA: number) => {
    const made = (twoPM || 0) + (TPM || 0);
    const att = (twoPA || 0) + (TPA || 0);
    return att > 0 ? `${made}/${att}` : "0/0";
  };

  const calculateFGPct = (twoPM: number, twoPA: number, TPM: number, TPA: number) => {
    const made = (twoPM || 0) + (TPM || 0);
    const att = (twoPA || 0) + (TPA || 0);
    return att > 0 ? ((made / att) * 100).toFixed(1) : ".000";
  };

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono border-collapse border-2 border-black">
        <thead>
          <tr className="border-b-2 border-black bg-gray-100">
            <th className="text-left p-2 font-bold">DATE</th>
            <th className="text-left p-2 font-bold">OPP</th>
            <th className="text-center p-2 font-bold">MIN</th>
            <th className="text-center p-2 font-bold">PTS</th>
            <th className="text-center p-2 font-bold">REB</th>
            <th className="text-center p-2 font-bold">AST</th>
            <th className="text-center p-2 font-bold">STL</th>
            <th className="text-center p-2 font-bold">BLK</th>
            <th className="text-center p-2 font-bold">FG</th>
            <th className="text-center p-2 font-bold">3PT</th>
            <th className="text-center p-2 font-bold">FT</th>
            <th className="text-center p-2 font-bold">PF</th>
            <th className="text-center p-2 font-bold">BPM</th>
          </tr>
        </thead>
        <tbody>
          {games.map((game, index) => (
            <tr 
              key={`${game.numdate}-${index}`}
              className={`border-b border-gray-200 hover:bg-gray-50 ${
                game.win2 === 1 ? "bg-green-50" : "bg-red-50"
              }`}
            >
              <td className="p-2">
                <div className="font-bold">{game.datetext}</div>
                <div className="text-[9px] text-gray-600">
                  {game.loc === "H" ? "vs" : game.loc === "A" ? "@" : "N"}
                </div>
              </td>
              <td className="p-2 font-bold">{game.opponent}</td>
              <td className="text-center p-2">{game.Min_per?.toFixed(1)}</td>
              <td className="text-center p-2 font-bold">{game.pts}</td>
              <td className="text-center p-2">{(game.ORB + game.DRB).toFixed(1)}</td>
              <td className="text-center p-2">{game.AST?.toFixed(1)}</td>
              <td className="text-center p-2">{game.STL?.toFixed(1)}</td>
              <td className="text-center p-2">{game.BLK?.toFixed(1)}</td>
              <td className="text-center p-2">
                <div>{calculateFG(game.twoPM, game.twoPA, game.TPM, game.TPA)}</div>
                <div className="text-[9px] text-gray-600">{calculateFGPct(game.twoPM, game.twoPA, game.TPM, game.TPA)}</div>
              </td>
              <td className="text-center p-2">
                <div>{game.TPM || 0}/{game.TPA || 0}</div>
                <div className="text-[9px] text-gray-600">
                  {game.TPA > 0 ? ((game.TPM / game.TPA) * 100).toFixed(1) : ".000"}
                </div>
              </td>
              <td className="text-center p-2">
                <div>{game.FTM || 0}/{game.FTA || 0}</div>
                <div className="text-[9px] text-gray-600">
                  {game.FTA > 0 ? ((game.FTM / game.FTA) * 100).toFixed(1) : ".000"}
                </div>
              </td>
              <td className="text-center p-2">{game.PF?.toFixed(1)}</td>
              <td className={`text-center p-2 font-bold ${game.bpm >= 0 ? "text-green-600" : "text-red-600"}`}>
                {game.bpm >= 0 ? "+" : ""}{game.bpm?.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
      <div className="mt-4 text-center">
        <Link
          href={`/player/${playerId}/games?year=${yearToUse}`}
          className="inline-block px-4 py-2 border-2 border-black bg-[#E7E8D1] text-black font-bold text-xs hover:bg-[#c7d0b8] transition-colors"
        >
          VIEW GAME LOG
        </Link>
      </div>
    </div>
  );
}
