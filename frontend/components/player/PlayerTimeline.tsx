"use client";

import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";

type PlayerTimelineProps = {
  playerHistory: any[];
  playerName: string;
  currentYear?: string | number | null;
};

export default function PlayerTimeline({
  playerHistory,
  playerName,
  currentYear,
}: PlayerTimelineProps) {
  // Sort history by year
  const sortedHistory = [...playerHistory].sort((a, b) => a.year - b.year);

  // Get unique teams and positions
  const teamChanges = sortedHistory.map((year) => ({
    year: year.year,
    team: year.team,
    conf: year.conf,
    position: year.Position || year["roster.pos"] || "N/A",
  }));

  return (
    <Panel>
      <PanelHeader>PLAYER TIMELINE</PanelHeader>

      {/* Overview */}
      <div className="p-4 space-y-4">
        <div className="text-sm">
          <p className="font-bold mb-2">Career Overview</p>
          <p>
            {playerName} has played {sortedHistory.length} season{sortedHistory.length !== 1 ? "s" : ""} across{" "}
            {new Set(teamChanges.map((t) => t.team)).size} team{new Set(teamChanges.map((t) => t.team)).size !== 1 ? "s" : ""}.
          </p>
        </div>

        {/* Quick Timeline */}
        <div className="border-l-2 border-black pl-4 space-y-3">
          {teamChanges.map((item) => {
            const isCurrentYear = String(currentYear) === String(item.year);
            return (
              <div key={item.year} className="relative">
                <div 
                  className={`absolute -left-[21px] top-1 w-3 h-3 rounded-full ${
                    isCurrentYear ? "bg-red-600" : "bg-black"
                  }`} 
                />
                <div className={`text-xs ${isCurrentYear ? "font-bold" : ""}`}>
                  <p className="font-bold">{item.year}</p>
                  <p className="text-gray-700">{item.team} ({item.conf})</p>
                  <p className="text-gray-600">Position: {item.position}</p>
                  {isCurrentYear && (
                    <p className="text-red-600 text-[10px] mt-1">CURRENT SEASON</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Panel>
  );
}
