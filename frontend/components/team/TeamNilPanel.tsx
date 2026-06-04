"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface NilBreakdown {
  position_rank: number;
  win_shares: number;
  bpm_percentile: number;
  team_success: number;
  conference_prestige: number;
  cluster_quality: number;
  total_score: number;
}

interface NilValuation {
  ncaa_id: string;
  player_name: string;
  team: string;
  position: string;
  year: string;
  nil_score: number;
  estimated_value_low: number;
  estimated_value_high: number;
  percentile_all: number;
  percentile_position: number;
  cluster_id?: number | string;
  cluster_description?: string;
  breakdown: NilBreakdown;
}

interface TeamNilPanelProps {
  teamId: string;
  year?: number | null | string;
}

const POSITION_TYPE_MAP: { [key: string]: string } = {
  "PG": "Guard",
  "SG": "Guard",
  "CG": "Guard",
  "WG": "Guard",
  "s-PG": "Guard",
  "G": "Guard",
  "SF": "Forward",
  "PF": "Forward",
  "WF": "Forward",
  "S-PF": "Forward",
  "F": "Forward",
  "C": "Big",
  "PF/C": "Big",
};

const getPositionType = (position: string): string => {
  return POSITION_TYPE_MAP[position] || "Forward";
};

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];

export default function TeamNilPanel({ teamId, year }: TeamNilPanelProps) {
  const [nilData, setNilData] = useState<NilValuation[] | null>(null);
  const [totalTeamValue, setTotalTeamValue] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredPlayer, setHoveredPlayer] = useState<NilValuation | null>(null);
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  const [pinnedPlayer, setPinnedPlayer] = useState<NilValuation | null>(null);

  useEffect(() => {
    if (!teamId) return;

    setLoading(true);
    setError(null);

    const yearParam = year ? `?year=${year}` : "";
    fetch(`/api/v1/nil/teams/${teamId}${yearParam}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setNilData(data.valuations);
          setTotalTeamValue(data.total_team_value || 0);
        } else {
          setError("Failed to load NIL data");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to load NIL data");
        setLoading(false);
      });
  }, [teamId, year]);

  // Clear pinned player when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest("table") && pinnedPlayer) {
        setPinnedPlayer(null);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [pinnedPlayer]);

  if (loading) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-sm">Loading NIL valuations...</p>
        </div>
      </div>
    );
  }

  if (error || !nilData || nilData.length === 0) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-sm mb-2">NIL valuations not available</p>
          <p className="text-xs">No NIL data for this team</p>
        </div>
      </div>
    );
  }

  const formatDollars = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    } else {
      return `$${value.toFixed(0)}`;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-blue-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-600";
  };

  // Group by position type
  const groupedData = nilData.reduce((acc, player) => {
    const posType = getPositionType(player.position);
    if (!acc[posType]) {
      acc[posType] = [];
    }
    acc[posType].push(player);
    return acc;
  }, {} as { [key: string]: NilValuation[] });

  // Prepare pie chart data
  const pieData = Object.entries(groupedData).map(([posType, players]) => ({
    name: posType,
    value: players.reduce((sum, p) => sum + p.estimated_value_high, 0),
  }));

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-4 font-mono">
      <div className="flex justify-between items-center border-b border-black pb-2 mb-3">
        <div className="font-bold text-sm">
          NIL VALUATIONS ({nilData.length} players)
        </div>
        <div className="text-sm font-bold">
          Total: {formatDollars(totalTeamValue)}
        </div>
      </div>

      <div className="flex gap-4">
        {/* Pie Chart - Left Side */}
        <div className="w-48 flex-shrink-0">
          <div className="text-[10px] font-bold mb-2 text-center">Distribution</div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={30}
                  outerRadius={50}
                  paddingAngle={5}
                  dataKey="value"
                  label={(entry) => entry.name}
                  labelLine={false}
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Table - Right Side */}
        <div className="flex-1 overflow-x-auto relative">
          <table className="w-full text-[10px] border-collapse">
            <thead>
              <tr className="border-b border-black">
                <th className="text-left py-1 px-2">Player</th>
                <th className="text-center py-1 px-2">Pos</th>
                <th className="text-center py-1 px-2">Score</th>
                <th className="text-center py-1 px-2">BPM%</th>
                <th className="text-center py-1 px-2">Value</th>
                <th className="text-center py-1 px-2">Cluster</th>
              </tr>
            </thead>
            <tbody>
              {nilData.map((player) => (
                <tr
                  key={player.ncaa_id}
                  className={`border-b border-black/20 cursor-pointer hover:bg-black/5 ${pinnedPlayer?.ncaa_id === player.ncaa_id ? "bg-black/10" : ""}`}
                  onMouseEnter={(e) => {
                    if (!pinnedPlayer) {
                      setHoveredPlayer(player);
                      setMousePosition({ x: e.clientX, y: e.clientY });
                    }
                  }}
                  onMouseLeave={() => {
                    if (!pinnedPlayer) {
                      setHoveredPlayer(null);
                      setMousePosition(null);
                    }
                  }}
                  onClick={(e) => {
                    if (pinnedPlayer?.ncaa_id === player.ncaa_id) {
                      setPinnedPlayer(null);
                    } else {
                      setPinnedPlayer(player);
                      setMousePosition({ x: e.clientX, y: e.clientY });
                    }
                  }}
                >
                  <td className="py-1 px-2">
                    <div className="font-medium">{player.player_name}</div>
                  </td>
                  <td className="text-center py-1 px-2">{player.position}</td>
                  <td className={`text-center py-1 px-2 ${getScoreColor(player.nil_score)}`}>
                    {player.nil_score.toFixed(1)}
                  </td>
                  <td className="text-center py-1 px-2">
                    {player.breakdown?.bpm_percentile?.toFixed(0) || "-"}
                  </td>
                  <td className="text-center py-1 px-2">
                    {formatDollars(player.estimated_value_high)}
                  </td>
                  <td className="text-center py-1 px-2 text-[9px]">
                    {player.cluster_description || "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Hover Tooltip */}
        {(hoveredPlayer || pinnedPlayer) && mousePosition && (
          <div
            className="fixed bg-white border-2 border-black p-3 shadow-lg z-50 w-48 text-[10px] font-mono pointer-events-none"
            style={{ left: mousePosition.x + 10, top: mousePosition.y + 10 }}
          >
            <div className="font-bold border-b border-black pb-1 mb-2">
              {(pinnedPlayer || hoveredPlayer)?.player_name}
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Pos Rank:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.position_rank?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span>Win Shares:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.win_shares?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span>BPM%:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.bpm_percentile?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span>Team Success:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.team_success?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span>Conf Prestige:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.conference_prestige?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span>Cluster Quality:</span>
                <span className="font-medium">{(pinnedPlayer || hoveredPlayer)?.breakdown?.cluster_quality?.toFixed(1) ?? "-"}</span>
              </div>
              <div className="border-t border-black pt-1 mt-1 flex justify-between font-bold">
                <span>Total:</span>
                <span>{(pinnedPlayer || hoveredPlayer)?.breakdown?.total_score?.toFixed(1) ?? "-"}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
