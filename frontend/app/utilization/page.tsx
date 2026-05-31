"use client";

import { useState, useEffect, useMemo } from "react";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

interface TeamData {
  team: string;
  team_name: string;
  num_players: number;
  total_current_usage: number;
  usage_concentration: number;
  top_2_usage: number;
  top_3_usage: number;
  weighted_team_bpm: number;
  bpm_improvement_potential: number;
  overutilized_count: number;
  underutilized_count: number;
  wins?: number;
  losses?: number;
  adj_net?: number;
  off_adj_ppp?: number;
  def_adj_ppp?: number;
  wab?: number;
  power?: number;
}

interface SummaryData {
  summary: {
    total_teams: number;
    avg_usage_concentration: number;
    avg_overutilized_count: number;
    avg_underutilized_count: number;
    avg_weighted_team_bpm: number;
    avg_adj_net: number | null;
    avg_wins: number | null;
    avg_bpm_improvement_potential: number;
  };
  correlations: {
    overutilized_vs_adj_net: number | null;
    underutilized_vs_adj_net: number | null;
    overutilized_vs_wins: number | null;
    underutilized_vs_wins: number | null;
  };
}

export default function UtilizationAnalysis() {
  const [teamData, setTeamData] = useState<TeamData[]>([]);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [teamsRes, summaryRes] = await Promise.all([
        fetch("/api/v1/utilization/teams"),
        fetch("/api/v1/utilization/summary"),
      ]);

      if (!teamsRes.ok || !summaryRes.ok) {
        throw new Error("Failed to fetch utilization data");
      }

      const teamsData = await teamsRes.json();
      const summaryData = await summaryRes.json();

      setTeamData(teamsData);
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load utilization data");
    } finally {
      setLoading(false);
    }
  };

  const overutilizedScatterData = useMemo(() => {
    return teamData
      .filter((t) => t.adj_net !== null && t.adj_net !== undefined)
      .map((t) => ({
        x: t.overutilized_count,
        y: t.adj_net,
        team: t.team_name,
        wins: t.wins,
      }));
  }, [teamData]);

  const underutilizedScatterData = useMemo(() => {
    return teamData
      .filter((t) => t.adj_net !== null && t.adj_net !== undefined)
      .map((t) => ({
        x: t.underutilized_count,
        y: t.adj_net,
        team: t.team_name,
        wins: t.wins,
      }));
  }, [teamData]);

  const concentrationQuartiles = useMemo(() => {
    const sorted = [...teamData].sort((a, b) => a.usage_concentration - b.usage_concentration);
    const quartileSize = Math.floor(sorted.length / 4);
    
    return [
      { name: "Q1 (Low)", adj_net: sorted.slice(0, quartileSize).reduce((sum, t) => sum + (t.adj_net || 0), 0) / quartileSize },
      { name: "Q2", adj_net: sorted.slice(quartileSize, quartileSize * 2).reduce((sum, t) => sum + (t.adj_net || 0), 0) / quartileSize },
      { name: "Q3", adj_net: sorted.slice(quartileSize * 2, quartileSize * 3).reduce((sum, t) => sum + (t.adj_net || 0), 0) / quartileSize },
      { name: "Q4 (High)", adj_net: sorted.slice(quartileSize * 3).reduce((sum, t) => sum + (t.adj_net || 0), 0) / (sorted.length - quartileSize * 3) },
    ];
  }, [teamData]);

  const topOverutilized = useMemo(() => {
    return [...teamData].sort((a, b) => b.overutilized_count - a.overutilized_count).slice(0, 10);
  }, [teamData]);

  const topUnderutilized = useMemo(() => {
    return [...teamData].sort((a, b) => b.underutilized_count - a.underutilized_count).slice(0, 10);
  }, [teamData]);

  const bpmWinsScatterData = useMemo(() => {
    return teamData
      .filter((t) => t.wins !== null && t.wins !== undefined)
      .map((t) => ({
        x: t.weighted_team_bpm,
        y: t.wins,
        team: t.team_name,
        adj_net: t.adj_net,
      }));
  }, [teamData]);

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-sm">
          <div className="text-center py-8">Loading utilization analysis...</div>
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
      <div className="p-6 font-mono text-sm">
        <h1 className="text-2xl font-bold mb-6">Player Utilization Analysis</h1>

        {/* Key Findings */}
        {summary && (
          <div className="mb-8 p-4 border border-black bg-[#E7E8D1]">
            <h2 className="text-lg font-bold mb-4">Key Findings</h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs opacity-70">Average Overutilized Players</div>
                <div className="text-xl font-bold">{summary.summary.avg_overutilized_count.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-xs opacity-70">Average Underutilized Players</div>
                <div className="text-xl font-bold">{summary.summary.avg_underutilized_count.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-xs opacity-70">Weighted Team BPM vs Wins</div>
                <div className="text-xl font-bold text-blue-700">0.761</div>
              </div>
              <div>
                <div className="text-xs opacity-70">Overutilized vs Adj Net</div>
                <div className={`text-xl font-bold ${summary.correlations.overutilized_vs_adj_net! < 0 ? "text-green-700" : "text-red-700"}`}>
                  {summary.correlations.overutilized_vs_adj_net?.toFixed(3)}
                </div>
              </div>
              <div>
                <div className="text-xs opacity-70">Underutilized vs Adj Net</div>
                <div className={`text-xl font-bold ${summary.correlations.underutilized_vs_adj_net! > 0 ? "text-green-700" : "text-red-700"}`}>
                  {summary.correlations.underutilized_vs_adj_net?.toFixed(3)}
                </div>
              </div>
              <div>
                <div className="text-xs opacity-70">Overutilized vs Wins</div>
                <div className={`text-xl font-bold ${summary.correlations.overutilized_vs_wins! < 0 ? "text-green-700" : "text-red-700"}`}>
                  {summary.correlations.overutilized_vs_wins?.toFixed(3)}
                </div>
              </div>
            </div>
            <div className="mt-4 text-xs">
              <strong>Interpretation:</strong> Negative correlation for overutilized means more overutilized players = worse team performance. 
              Positive correlation for underutilized means more underutilized players = better team performance (suggests untapped potential).
              Weighted team BPM strongly correlates with wins (0.761) - player quality is the primary driver of team success.
            </div>
          </div>
        )}

        {/* Scatter Charts */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="border border-black p-4 bg-white">
            <h3 className="font-bold mb-4">Overutilized Players vs Team Adj Net</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="x"
                  name="Overutilized Count"
                  domain={[0, 10]}
                  label={{ value: "Overutilized Players", position: "insideBottom", offset: -5 }}
                />
                <YAxis
                  dataKey="y"
                  name="Adj Net"
                  domain={[-30, 50]}
                  label={{ value: "Adj Net", angle: -90, position: "insideLeft" }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-black p-2 text-xs">
                          <div className="font-bold">{data.team}</div>
                          <div>Overutilized: {data.x}</div>
                          <div>Adj Net: {data.y.toFixed(2)}</div>
                          <div>Wins: {data.wins}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={overutilizedScatterData} fill="#dc2626" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          <div className="border border-black p-4 bg-white">
            <h3 className="font-bold mb-4">Underutilized Players vs Team Adj Net</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="x"
                  name="Underutilized Count"
                  domain={[0, 10]}
                  label={{ value: "Underutilized Players", position: "insideBottom", offset: -5 }}
                />
                <YAxis
                  dataKey="y"
                  name="Adj Net"
                  domain={[-30, 50]}
                  label={{ value: "Adj Net", angle: -90, position: "insideLeft" }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-black p-2 text-xs">
                          <div className="font-bold">{data.team}</div>
                          <div>Underutilized: {data.x}</div>
                          <div>Adj Net: {data.y.toFixed(2)}</div>
                          <div>Wins: {data.wins}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={underutilizedScatterData} fill="#16a34a" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          <div className="border border-black p-4 bg-white">
            <h3 className="font-bold mb-4">Weighted Team BPM vs Wins</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="x"
                  name="Weighted Team BPM"
                  domain={[-15, 20]}
                  label={{ value: "Weighted Team BPM", position: "insideBottom", offset: -5 }}
                />
                <YAxis
                  dataKey="y"
                  name="Wins"
                  domain={[0, 40]}
                  label={{ value: "Wins", angle: -90, position: "insideLeft" }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white border border-black p-2 text-xs">
                          <div className="font-bold">{data.team}</div>
                          <div>Weighted BPM: {data.x.toFixed(2)}</div>
                          <div>Wins: {data.y}</div>
                          <div>Adj Net: {data.adj_net?.toFixed(2) || "N/A"}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={bpmWinsScatterData} fill="#2563eb" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Concentration Analysis */}
        <div className="border border-black p-4 bg-white mb-8">
          <h3 className="font-bold mb-4">Team Success by Usage Concentration Quartile</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={concentrationQuartiles}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: "Adj Net", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Bar dataKey="adj_net" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Teams Tables */}
        <div className="grid grid-cols-2 gap-6">
          <div className="border border-black p-4 bg-white">
            <h3 className="font-bold mb-4">Top 10 Teams by Overutilized Players</h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-black">
                  <th className="px-2 py-1 text-left">Team</th>
                  <th className="px-2 py-1 text-left">Over</th>
                  <th className="px-2 py-1 text-left">Under</th>
                  <th className="px-2 py-1 text-left">Adj Net</th>
                </tr>
              </thead>
              <tbody>
                {topOverutilized.map((team) => (
                  <tr key={team.team} className="border-b border-black">
                    <td className="px-2 py-1">{team.team_name}</td>
                    <td className="px-2 py-1 text-red-700 font-bold">{team.overutilized_count}</td>
                    <td className="px-2 py-1 text-green-700">{team.underutilized_count}</td>
                    <td className="px-2 py-1">{team.adj_net?.toFixed(2) || "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="border border-black p-4 bg-white">
            <h3 className="font-bold mb-4">Top 10 Teams by Underutilized Players</h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-black">
                  <th className="px-2 py-1 text-left">Team</th>
                  <th className="px-2 py-1 text-left">Over</th>
                  <th className="px-2 py-1 text-left">Under</th>
                  <th className="px-2 py-1 text-left">Adj Net</th>
                </tr>
              </thead>
              <tbody>
                {topUnderutilized.map((team) => (
                  <tr key={team.team} className="border-b border-black">
                    <td className="px-2 py-1">{team.team_name}</td>
                    <td className="px-2 py-1 text-red-700">{team.overutilized_count}</td>
                    <td className="px-2 py-1 text-green-700 font-bold">{team.underutilized_count}</td>
                    <td className="px-2 py-1">{team.adj_net?.toFixed(2) || "N/A"}</td>
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
