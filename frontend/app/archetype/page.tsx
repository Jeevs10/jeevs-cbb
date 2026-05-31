"use client";

import { useState, useEffect, useMemo } from "react";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell,
} from "recharts";

const ARCHETYPE_LABELS: Record<string, string> = {
  PG: "Point Guard",
  CG: "Combo Guard",
  WG: "Wing Guard",
  "s-PG": "Scoring Guard",
  WF: "Wing Forward",
  "S-PF": "Stretch Forward",
  "PF/C": "Hybrid Big",
  C: "Center",
};

interface TeamData {
  team: string;
  team_name: string;
  total_minutes: number;
  total_players: number;
  weighted_team_bpm: number;
  wins?: number;
  losses?: number;
  adj_net?: number;
  off_adj_ppp?: number;
  def_adj_ppp?: number;
  pct_minutes_PG?: number;
  pct_minutes_CG?: number;
  pct_minutes_WG?: number;
  pct_minutes_s_PG?: number;
  pct_minutes_WF?: number;
  pct_minutes_S_PF?: number;
  pct_minutes_PF_C?: number;
  pct_minutes_C?: number;
}

interface CorrelationData {
  Comparison: string;
  Correlation: number;
}

interface SummaryData {
  total_teams: number;
  top_quartile_count: number;
  bottom_quartile_count: number;
  top_composition: Record<string, number>;
  bottom_composition: Record<string, number>;
  differences: Record<string, number>;
}

export default function ArchetypeAnalysis() {
  const [teamData, setTeamData] = useState<TeamData[]>([]);
  const [correlations, setCorrelations] = useState<CorrelationData[]>([]);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [teamsRes, correlationsRes, summaryRes] = await Promise.all([
        fetch("/api/v1/archetype/teams"),
        fetch("/api/v1/archetype/correlations"),
        fetch("/api/v1/archetype/summary"),
      ]);

      if (!teamsRes.ok || !correlationsRes.ok || !summaryRes.ok) {
        throw new Error("Failed to fetch archetype data");
      }

      const teamsData = await teamsRes.json();
      const correlationsData = await correlationsRes.json();
      const summaryData = await summaryRes.json();

      setTeamData(teamsData);
      setCorrelations(correlationsData);
      setSummary(summaryData);
      
      // Select top team by default
      if (teamsData.length > 0) {
        setSelectedTeam(teamsData[0].team_name);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load archetype data");
    } finally {
      setLoading(false);
    }
  };

  const correlationChartData = useMemo(() => {
    return correlations
      .filter((c) => c.Comparison.includes("vs adj_net"))
      .map((c) => {
        const archetype = c.Comparison.split(" vs ")[0];
        return {
          archetype: ARCHETYPE_LABELS[archetype] || archetype,
          correlation: c.Correlation,
          color: c.Correlation > 0 ? "#10B981" : "#EF4444",
        };
      })
      .sort((a, b) => b.correlation - a.correlation);
  }, [correlations]);

  const topBottomComparisonData = useMemo(() => {
    if (!summary) return [];
    return Object.keys(summary.differences).map((arch) => ({
      archetype: ARCHETYPE_LABELS[arch] || arch,
      top: summary.top_composition[arch] * 100,
      bottom: summary.bottom_composition[arch] * 100,
      difference: summary.differences[arch] * 100,
    }));
  }, [summary]);

  const selectedTeamData = useMemo(() => {
    if (!selectedTeam) return null;
    return teamData.find((t) => t.team_name === selectedTeam);
  }, [teamData, selectedTeam]);

  const selectedTeamRadarData = useMemo(() => {
    if (!selectedTeamData) return [];
    return Object.keys(ARCHETYPE_LABELS).map((arch) => ({
      archetype: ARCHETYPE_LABELS[arch],
      value: (selectedTeamData[`pct_minutes_${arch}` as keyof TeamData] as number) * 100 || 0,
    }));
  }, [selectedTeamData]);

  const optimalCompositionData = useMemo(() => {
    if (!summary) return [];
    return Object.keys(summary.top_composition).map((arch) => ({
      archetype: ARCHETYPE_LABELS[arch] || arch,
      value: summary.top_composition[arch] * 100,
    }));
  }, [summary]);

  const topTeams = useMemo(() => {
    return [...teamData]
      .filter((t) => t.adj_net !== undefined && t.adj_net !== null)
      .sort((a, b) => (b.adj_net || 0) - (a.adj_net || 0))
      .slice(0, 20);
  }, [teamData]);

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-sm">
          <div className="text-center py-8">Loading archetype analysis...</div>
        </div>
      </ErrorBoundary>
    );
  }

  if (error) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-sm">
          <ErrorMessage message={error} onRetry={fetchData} />
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="p-6 font-mono text-sm bg-gray-50 min-h-screen">
        <h1 className="text-3xl font-bold mb-2 text-gray-900">Team Archetype Analysis</h1>
        <p className="text-gray-600 mb-8">Minutes-weighted composition analysis and optimal roster construction patterns</p>

        {/* Key Insights */}
        {summary && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Teams Analyzed</div>
              <div className="text-2xl font-bold text-gray-900">{summary.total_teams}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Top Quartile</div>
              <div className="text-2xl font-bold text-gray-900">{summary.top_quartile_count}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Bottom Quartile</div>
              <div className="text-2xl font-bold text-gray-900">{summary.bottom_quartile_count}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
              <div className="text-xs text-gray-500 uppercase tracking-wide">Archetypes</div>
              <div className="text-2xl font-bold text-gray-900">8</div>
            </div>
          </div>
        )}

        {/* Correlation Analysis */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Archetype Impact on Team Success</h2>
          <p className="text-sm text-gray-600 mb-4">
            Correlation between archetype minutes percentage and Adjusted Net Rating. 
            Positive values indicate that more minutes for that archetype correlates with better team performance.
          </p>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={correlationChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[-0.3, 0.3]} />
                <YAxis dataKey="archetype" type="category" width={120} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-3">
                          <div className="font-bold">{data.archetype}</div>
                          <div className="text-sm">Correlation: {data.correlation.toFixed(3)}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="correlation" radius={[0, 8, 8, 0]}>
                  {correlationChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top vs Bottom Quartile Comparison */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Successful vs Struggling Teams</h2>
          <p className="text-sm text-gray-600 mb-4">
            Comparison of archetype composition between top 25% and bottom 25% teams by Adjusted Net Rating.
          </p>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topBottomComparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="archetype" angle={-45} textAnchor="end" height={100} />
                <YAxis label={{ value: "Minutes %", angle: -90, position: "insideLeft" }} />
                <Tooltip />
                <Bar dataKey="top" name="Top Quartile" fill="#10B981" radius={[8, 8, 0, 0]} />
                <Bar dataKey="bottom" name="Bottom Quartile" fill="#EF4444" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Team Selector and Radar Chart */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900">Team Composition</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Team</label>
              <select
                value={selectedTeam || ""}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {topTeams.map((team) => (
                  <option key={team.team} value={team.team_name}>
                    {team.team_name} (Adj Net: {team.adj_net?.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>
            {selectedTeamData && (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Adjusted Net Rating:</span>
                  <span className="font-bold">{selectedTeamData.adj_net?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wins:</span>
                  <span className="font-bold">{selectedTeamData.wins}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Weighted Team BPM:</span>
                  <span className="font-bold">{selectedTeamData.weighted_team_bpm?.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900">Archetype Radar</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={selectedTeamRadarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="archetype" tick={{ fontSize: 10 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 50]} tick={{ fontSize: 8 }} />
                  <Radar
                    name="Team Composition"
                    dataKey="value"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.3}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Optimal Composition */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Optimal Team Composition</h2>
          <p className="text-sm text-gray-600 mb-4">
            Average archetype composition of top 25% teams by Adjusted Net Rating.
          </p>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={optimalCompositionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="archetype" angle={-45} textAnchor="end" height={100} />
                <YAxis label={{ value: "Minutes %", angle: -90, position: "insideLeft" }} />
                <Tooltip />
                <Bar dataKey="value" fill="#8B5CF6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Teams Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Top 20 Teams by Adjusted Net Rating</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="px-4 py-2 text-left">Team</th>
                  <th className="px-4 py-2 text-left">Adj Net</th>
                  <th className="px-4 py-2 text-left">Wins</th>
                  <th className="px-4 py-2 text-left">Weighted BPM</th>
                  <th className="px-4 py-2 text-left">PG</th>
                  <th className="px-4 py-2 text-left">CG</th>
                  <th className="px-4 py-2 text-left">WG</th>
                  <th className="px-4 py-2 text-left">WF</th>
                  <th className="px-4 py-2 text-left">C</th>
                </tr>
              </thead>
              <tbody>
                {topTeams.map((team) => (
                  <tr
                    key={team.team}
                    className={`border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                      selectedTeam === team.team_name ? "bg-blue-50" : ""
                    }`}
                    onClick={() => setSelectedTeam(team.team_name)}
                  >
                    <td className="px-4 py-2 font-medium">{team.team_name}</td>
                    <td className="px-4 py-2">{team.adj_net?.toFixed(2)}</td>
                    <td className="px-4 py-2">{team.wins}</td>
                    <td className="px-4 py-2">{team.weighted_team_bpm?.toFixed(2)}</td>
                    <td className="px-4 py-2">{((team.pct_minutes_PG || 0) * 100).toFixed(0)}%</td>
                    <td className="px-4 py-2">{((team.pct_minutes_CG || 0) * 100).toFixed(0)}%</td>
                    <td className="px-4 py-2">{((team.pct_minutes_WG || 0) * 100).toFixed(0)}%</td>
                    <td className="px-4 py-2">{((team.pct_minutes_WF || 0) * 100).toFixed(0)}%</td>
                    <td className="px-4 py-2">{((team.pct_minutes_C || 0) * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
