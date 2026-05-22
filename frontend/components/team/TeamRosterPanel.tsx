"use client";

import Link from "next/link";

interface RosterPlayer {
  Id: string;
  Sourceid: string | number;
  Jersey: string;
  FirstName: string;
  LastName: string;
  Position: string;
  Height: string;
  Weight: string;
  HometownCity: string;
  HometownState: string;
  Season?: string;
  PPG?: number;
  RPG?: number;
  APG?: number;
  PORPAG?: number;
}

interface TeamRosterPanelProps {
  roster?: RosterPlayer[];
  year?: number | null | "career";
}

function formatHeight(h?: string | number): string {
  if (!h) return "—";

  // Convert to string if it's a number
  const heightStr = String(h);

  const parts = heightStr.split("-");
  if (parts.length !== 2) return heightStr;

  const feet = parts[0];
  const inches = String(Number(parts[1]));

  return `${feet}'${inches}"`;
}

export default function TeamRosterPanel({ roster, year }: TeamRosterPanelProps) {
  if (!roster || roster.length === 0) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-sm mb-2">Roster not available</p>
          <p className="text-xs">No roster data for this team</p>
        </div>
      </div>
    );
  }

  // Filter roster by selected year
  let filteredRoster = roster;
  if (year === "career" || year === null || year === undefined) {
    // If year is "career", null, or undefined (Latest), show the most recent season's roster
    const seasons = roster
      .map(player => player.Season ? String(player.Season) : '')
      .filter(season => season !== '');
    
    if (seasons.length > 0) {
      const latestSeason = seasons.sort((a, b) => Number(b) - Number(a))[0];
      filteredRoster = roster.filter(player => {
        const playerSeason = player.Season ? String(player.Season) : '';
        return playerSeason === latestSeason;
      });
    }
  } else {
    // Filter by specific year
    filteredRoster = roster.filter(player => {
      const playerSeason = player.Season ? String(player.Season) : '';
      return playerSeason === String(year);
    });
  }

  // Deduplicate by player ID (Sourceid or Id) to handle duplicate entries
  const uniqueRoster = filteredRoster.filter((player, index, self) => {
    const playerId = player.Sourceid || player.Id;
    const firstIndex = self.findIndex(p => (p.Sourceid || p.Id) === playerId);
    return index === firstIndex;
  });

  if (uniqueRoster.length === 0) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-sm mb-2">No roster for this year</p>
          <p className="text-xs">Select a different year to see roster data</p>
        </div>
      </div>
    );
  }

  // Sort roster by PORPAG descending, players without PORPAG go to the end
  const sortedRoster = [...uniqueRoster].sort((a, b) => {
    const aPORPAG = a.PORPAG ?? -Infinity;
    const bPORPAG = b.PORPAG ?? -Infinity;
    return bPORPAG - aPORPAG;
  });

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono max-h-96 overflow-y-auto">
      <div className="border-b border-black pb-2 mb-3 font-bold text-xs sticky top-0 bg-[#C7D0B8]">
        ROSTER ({uniqueRoster.length} players)
      </div>
      
      <div className="space-y-1">
        {sortedRoster.map((player: RosterPlayer) => (
          <Link
            key={player.Sourceid || player.Id}
            href={`/player/${player.Sourceid || player.Id}`}
            className="block hover:bg-black/5 transition-colors"
          >
            <div className="flex items-center gap-2 py-1 px-2 text-xs">
              <div className="w-8 text-center font-bold">
                {player.Jersey || "—"}
              </div>
              <div className="flex-1">
                <div className="font-bold">
                  {player.FirstName} {player.LastName}
                </div>
                <div className="text-[10px] opacity-70">
                  {player.Position} • {formatHeight(player.Height)} • {player.Weight}lbs
                </div>
              </div>
              <div className="text-right text-[10px] font-mono opacity-70">
                {player.PPG !== null && player.PPG !== undefined && 
                 player.RPG !== null && player.RPG !== undefined && 
                 player.APG !== null && player.APG !== undefined ? (
                  <div>
                    {player.PPG.toFixed(1)} PPG • {player.RPG.toFixed(1)} RPG • {player.APG.toFixed(1)} APG
                  </div>
                ) : (
                  <div className="text-gray-400">No stats</div>
                )}
                {player.PORPAG !== null && player.PORPAG !== undefined && (
                  <div className="text-[9px]">
                    PORPAG: {player.PORPAG.toFixed(1)}
                  </div>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
