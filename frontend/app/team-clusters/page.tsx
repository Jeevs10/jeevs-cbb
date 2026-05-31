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

interface TeamCluster {
  team: string;
  team_name: string;
  team_cluster: number;
  pca_1: number;
  pca_2: number;
  weighted_team_bpm: number;
  adj_net: number;
  wins: number;
  pct_minutes_PG: number;
  pct_minutes_C: number;
  pct_minutes_WG: number;
}

interface ClusterDescription {
  cluster_id: number;
  count: number;
  avg_adj_net: number;
  avg_weighted_bpm: number;
  avg_wins: number;
  avg_pct_minutes_PG: number;
  avg_pct_minutes_C: number;
  avg_pct_minutes_WG: number;
}

const CLUSTER_COLORS = [
  "#3B82F6", // Blue
  "#10B981", // Green
  "#F59E0B", // Amber
  "#EF4444", // Red
  "#8B5CF6", // Purple
  "#EC4899", // Pink
];

const CLUSTER_NAMES = [
  "Balanced Offense",
  "Guard Heavy",
  "Big Heavy",
  "High Efficiency",
  "Three-Point Focused",
  "Transition Heavy",
];

export default function TeamClustersPage() {
  const [teamClusters, setTeamClusters] = useState<TeamCluster[]>([]);
  const [clusterDescriptions, setClusterDescriptions] = useState<ClusterDescription[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [clustersRes, descriptionsRes] = await Promise.all([
        fetch("/api/v1/team-clusters"),
        fetch("/api/v1/team-clusters/descriptions"),
      ]);

      if (!clustersRes.ok || !descriptionsRes.ok) {
        throw new Error("Failed to fetch team cluster data");
      }

      const clustersData = await clustersRes.json();
      const descriptionsData = await descriptionsRes.json();

      setTeamClusters(clustersData);
      setClusterDescriptions(descriptionsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load team clusters");
    } finally {
      setLoading(false);
    }
  };

  const scatterData = useMemo(() => {
    return teamClusters.map((team) => ({
      team: team.team_name,
      pca_1: team.pca_1,
      pca_2: team.pca_2,
      cluster: team.team_cluster,
      adj_net: team.adj_net,
      bpm: team.weighted_team_bpm,
    }));
  }, [teamClusters]);

  const filteredTeams = useMemo(() => {
    if (selectedCluster === null) return teamClusters;
    return teamClusters.filter((t) => t.team_cluster === selectedCluster);
  }, [teamClusters, selectedCluster]);

  const clusterBarData = useMemo(() => {
    return clusterDescriptions.map((desc) => ({
      cluster: CLUSTER_NAMES[desc.cluster_id] || `Cluster ${desc.cluster_id}`,
      count: desc.count,
      avg_adj_net: desc.avg_adj_net,
      avg_bpm: desc.avg_weighted_bpm,
    }));
  }, [clusterDescriptions]);

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-sm">
          <div className="text-center py-8">Loading team clusters...</div>
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
      <div className="p-8 font-mono text-sm bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2 text-slate-900 tracking-tight">Team Clustering</h1>
            <p className="text-slate-600 text-base">Team playstyle analysis based on archetype composition and performance metrics</p>
          </div>

          {/* Cluster Overview */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Total Teams</div>
              <div className="text-3xl font-bold text-slate-900">{teamClusters.length}</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Clusters</div>
              <div className="text-3xl font-bold text-slate-900">{clusterDescriptions.length}</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
              <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Selected Cluster</div>
              <div className="text-3xl font-bold text-slate-900">
                {selectedCluster !== null ? CLUSTER_NAMES[selectedCluster] : "All"}
              </div>
            </div>
          </div>

          {/* PCA Visualization */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200 mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Team Playstyle Map</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="pca_1" 
                    name="Offensive Style" 
                    label={{ value: 'Offensive Style', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    dataKey="pca_2" 
                    name="Efficiency" 
                    label={{ value: 'Efficiency', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200">
                            <div className="font-semibold text-slate-900">{data.team}</div>
                            <div className="text-xs text-slate-500">Cluster: {CLUSTER_NAMES[data.cluster]}</div>
                            <div className="text-xs text-slate-500">Adj Net: {data.adj_net?.toFixed(2)}</div>
                            <div className="text-xs text-slate-500">BPM: {data.bpm?.toFixed(2)}</div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  {clusterDescriptions.map((desc) => (
                    <Scatter
                      key={desc.cluster_id}
                      name={CLUSTER_NAMES[desc.cluster_id]}
                      data={scatterData.filter((d) => d.cluster === desc.cluster_id)}
                      fill={CLUSTER_COLORS[desc.cluster_id]}
                      opacity={selectedCluster === null || selectedCluster === desc.cluster_id ? 1 : 0.2}
                      onClick={() => setSelectedCluster(selectedCluster === desc.cluster_id ? null : desc.cluster_id)}
                      style={{ cursor: 'pointer' }}
                    />
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {clusterDescriptions.map((desc) => (
                <button
                  key={desc.cluster_id}
                  onClick={() => setSelectedCluster(selectedCluster === desc.cluster_id ? null : desc.cluster_id)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    selectedCluster === desc.cluster_id
                      ? 'bg-slate-900 text-white'
                      : selectedCluster === null
                      ? 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-50'
                      : 'bg-white border border-slate-300 text-slate-700 opacity-50 hover:opacity-100'
                  }`}
                >
                  {CLUSTER_NAMES[desc.cluster_id]} ({desc.count})
                </button>
              ))}
              {selectedCluster !== null && (
                <button
                  onClick={() => setSelectedCluster(null)}
                  className="px-3 py-1 rounded-full text-xs font-medium bg-slate-200 text-slate-700 hover:bg-slate-300"
                >
                  Clear Selection
                </button>
              )}
            </div>
          </div>

          {/* Cluster Statistics */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
              <h2 className="text-xl font-bold mb-4 text-slate-900">Cluster Sizes</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clusterBarData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="cluster" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3B82F6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
              <h2 className="text-xl font-bold mb-4 text-slate-900">Cluster Performance</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clusterBarData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="cluster" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="avg_adj_net" name="Avg Adj Net" fill="#10B981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Team List */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">
              {selectedCluster !== null ? `${CLUSTER_NAMES[selectedCluster]} Teams` : "All Teams"}
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-slate-200">
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">Team</th>
                    <th className="px-4 py-3 text-center font-semibold text-slate-900">Cluster</th>
                    <th className="px-4 py-3 text-center font-semibold text-slate-900">Adj Net</th>
                    <th className="px-4 py-3 text-center font-semibold text-slate-900">Weighted BPM</th>
                    <th className="px-4 py-3 text-center font-semibold text-slate-900">Wins</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTeams.map((team) => (
                    <tr key={team.team} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-4 py-3 text-slate-900 font-medium">{team.team_name}</td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className="px-2 py-1 rounded-full text-xs font-medium"
                          style={{
                            backgroundColor: CLUSTER_COLORS[team.team_cluster] + '20',
                            color: CLUSTER_COLORS[team.team_cluster],
                          }}
                        >
                          {CLUSTER_NAMES[team.team_cluster]}
                        </span>
                      </td>
                      <td className={`px-4 py-3 text-center font-semibold ${team.adj_net > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {team.adj_net?.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-center text-slate-900">{team.weighted_team_bpm?.toFixed(2)}</td>
                      <td className="px-4 py-3 text-center text-slate-900">{team.wins}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
