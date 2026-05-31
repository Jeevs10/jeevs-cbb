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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const CLUSTER_COLORS = [
  "#3B82F6", // blue
  "#10B981", // green
  "#F59E0B", // amber
  "#EF4444", // red
  "#8B5CF6", // purple
  "#06B6D4", // cyan
];

interface ClusterDescription {
  cluster_id: number;
  count: number;
  avg_height: number;
  avg_usage: number;
  avg_rim_freq: number;
  avg_3pt_pct: number;
  avg_bpm: number;
  top_players: Array<{ Name: string; Team: string; BPM: number }>;
}

interface ClusterPlayer {
  Name: string;
  Team: string;
  cluster: number;
  pca_1: number;
  pca_2: number;
  BPM: number;
  Usage: number;
  OffensiveRating: number;
  DefensiveRating: number;
}

interface TeamClusterData {
  team: string;
  total_players: number;
  clusters: Record<number, number>;
  cluster_pcts: Record<number, number>;
}

export default function ClusterAnalysis() {
  const [clusterDescriptions, setClusterDescriptions] = useState<ClusterDescription[]>([]);
  const [clusterPlayers, setClusterPlayers] = useState<ClusterPlayer[]>([]);
  const [teamClusters, setTeamClusters] = useState<TeamClusterData[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [descriptionsRes, playersRes, teamsRes] = await Promise.all([
        fetch("/api/v1/clusters/descriptions"),
        fetch("/api/v1/clusters/players"),
        fetch("/api/v1/clusters/teams"),
      ]);

      if (!descriptionsRes.ok || !playersRes.ok || !teamsRes.ok) {
        throw new Error("Failed to fetch cluster data");
      }

      const descriptionsData = await descriptionsRes.json();
      const playersData = await playersRes.json();
      const teamsData = await teamsRes.json();

      setClusterDescriptions(descriptionsData);
      setClusterPlayers(playersData);
      setTeamClusters(teamsData);
      
      // Select first cluster by default
      if (descriptionsData.length > 0) {
        setSelectedCluster(descriptionsData[0].cluster_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cluster data");
    } finally {
      setLoading(false);
    }
  };

  const scatterData = useMemo(() => {
    return clusterPlayers.map((player) => ({
      x: player.pca_1,
      y: player.pca_2,
      cluster: player.cluster,
      name: player.Name,
      team: player.Team,
      bpm: player.BPM,
    }));
  }, [clusterPlayers]);

  const clusterCentroids = useMemo(() => {
    const centroids: Record<number, { x: number; y: number }> = {};
    clusterDescriptions.forEach((desc) => {
      const clusterPlayersData = clusterPlayers.filter((p) => p.cluster === desc.cluster_id);
      if (clusterPlayersData.length > 0) {
        const avgX = clusterPlayersData.reduce((sum, p) => sum + p.pca_1, 0) / clusterPlayersData.length;
        const avgY = clusterPlayersData.reduce((sum, p) => sum + p.pca_2, 0) / clusterPlayersData.length;
        centroids[desc.cluster_id] = { x: avgX, y: avgY };
      }
    });
    return centroids;
  }, [clusterPlayers, clusterDescriptions]);

  const clusterSizeData = useMemo(() => {
    return clusterDescriptions.map((desc) => ({
      cluster: `Cluster ${desc.cluster_id}`,
      count: desc.count,
      avg_bpm: desc.avg_bpm,
    }));
  }, [clusterDescriptions]);

  const selectedClusterPlayers = useMemo(() => {
    if (selectedCluster === null) return [];
    return clusterPlayers.filter((p) => p.cluster === selectedCluster);
  }, [clusterPlayers, selectedCluster]);

  const selectedTeamData = useMemo(() => {
    if (!selectedTeam) return null;
    return teamClusters.find((t) => t.team === selectedTeam);
  }, [teamClusters, selectedTeam]);

  const selectedTeamClusterData = useMemo(() => {
    if (!selectedTeamData) return [];
    return Object.keys(selectedTeamData.cluster_pcts).map((clusterId) => ({
      cluster: `Cluster ${clusterId}`,
      value: (selectedTeamData.cluster_pcts[parseInt(clusterId)] || 0) * 100,
    }));
  }, [selectedTeamData]);

  const clusterComparisonData = useMemo(() => {
    return clusterDescriptions.map((desc) => ({
      cluster: `Cluster ${desc.cluster_id}`,
      height: desc.avg_height,
      usage: desc.avg_usage,
      rim_freq: desc.avg_rim_freq,
      three_pt_pct: desc.avg_3pt_pct,
      bpm: desc.avg_bpm,
    }));
  }, [clusterDescriptions]);

  const topTeams = useMemo(() => {
    return [...teamClusters].sort((a, b) => b.total_players - a.total_players).slice(0, 20);
  }, [teamClusters]);

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-sm">
          <div className="text-center py-8">Loading cluster analysis...</div>
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
            <h1 className="text-4xl font-bold mb-2 text-slate-900 tracking-tight">Player Cluster Analysis</h1>
            <p className="text-slate-600 text-base">Data-driven player segmentation based on playstyle features using K-means clustering</p>
          </div>

        {/* Key Insights */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Total Players</div>
            <div className="text-3xl font-bold text-slate-900">{clusterPlayers.length}</div>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Clusters</div>
            <div className="text-3xl font-bold text-slate-900">{clusterDescriptions.length}</div>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Teams Analyzed</div>
            <div className="text-3xl font-bold text-slate-900">{teamClusters.length}</div>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Playstyle Features</div>
            <div className="text-3xl font-bold text-slate-900">18</div>
          </div>
        </div>

        {/* Cluster Cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-slate-900">Player Clusters</h2>
          <div className="grid grid-cols-3 gap-4">
            {clusterDescriptions.map((desc) => (
              <div
                key={desc.cluster_id}
                className={`bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-5 border-2 cursor-pointer transition-all hover:shadow-xl ${
                  selectedCluster === desc.cluster_id
                    ? 'border-blue-500 ring-2 ring-blue-500/20'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
                onClick={() => setSelectedCluster(desc.cluster_id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length] }}
                    />
                    <h3 className="font-bold text-slate-900">Cluster {desc.cluster_id}</h3>
                  </div>
                  <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-full">{desc.count} players</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Height:</span>
                    <span className="font-semibold text-slate-900">{desc.avg_height.toFixed(0)}"</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Usage:</span>
                    <span className="font-semibold text-slate-900">{desc.avg_usage.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Rim Frequency:</span>
                    <span className="font-semibold text-slate-900">{desc.avg_rim_freq.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">3PT Attempt Rate:</span>
                    <span className="font-semibold text-slate-900">{desc.avg_3pt_pct.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Avg BPM:</span>
                    <span className={`font-semibold ${desc.avg_bpm > 0 ? 'text-green-600' : 'text-red-600'}`}>{desc.avg_bpm.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* PCA Scatter Plot */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 mb-8 border border-slate-200">
          <h2 className="text-xl font-bold mb-2 text-slate-900">Playstyle Similarity Map</h2>
          <p className="text-sm text-slate-600 mb-4">
            Players with similar playstyles are grouped together. The X-axis represents the primary playstyle dimension (height vs shooting), while the Y-axis represents the secondary dimension (usage vs rim play). Click on a cluster to highlight it.
          </p>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="x" 
                  label={{ value: 'Size/Physicality → Shooting', position: 'insideBottom', offset: -5, style: { fontSize: 12, fill: '#64748b' } }}
                  stroke="#64748b" 
                />
                <YAxis 
                  dataKey="y" 
                  label={{ value: 'Low Usage → High Usage', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#64748b' } }}
                  stroke="#64748b" 
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const clusterDesc = clusterDescriptions.find(c => c.cluster_id === data.cluster);
                      return (
                        <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-4 min-w-[200px]">
                          <div className="font-bold text-slate-900 mb-2">{data.name}</div>
                          <div className="text-sm text-slate-600 mb-1">Team: {data.team}</div>
                          <div className="text-sm text-slate-600 mb-1">BPM: <span className={data.bpm > 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>{data.bpm.toFixed(2)}</span></div>
                          <div className="text-sm text-slate-600 mb-1">Cluster: {data.cluster}</div>
                          {clusterDesc && (
                            <div className="mt-2 pt-2 border-t border-slate-200">
                              <div className="text-xs text-slate-500">Cluster {data.cluster} Profile:</div>
                              <div className="text-xs text-slate-600">Height: {clusterDesc.avg_height.toFixed(0)}"</div>
                              <div className="text-xs text-slate-600">Usage: {clusterDesc.avg_usage.toFixed(1)}%</div>
                              <div className="text-xs text-slate-600">Rim Freq: {clusterDesc.avg_rim_freq.toFixed(1)}%</div>
                              <div className="text-xs text-slate-600">3PT: {clusterDesc.avg_3pt_pct.toFixed(1)}%</div>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                {clusterDescriptions.map((desc) => (
                  <Scatter
                    key={desc.cluster_id}
                    data={scatterData.filter((d) => d.cluster === desc.cluster_id)}
                    fill={CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length]}
                    fillOpacity={selectedCluster === null || selectedCluster === desc.cluster_id ? 0.7 : 0.2}
                    shape="circle"
                  />
                ))}
                {/* Cluster Centroids */}
                {Object.entries(clusterCentroids).map(([clusterId, centroid]) => (
                  <Scatter
                    key={`centroid-${clusterId}`}
                    data={[{ x: centroid.x, y: centroid.y, z: 50 }]}
                    fill={CLUSTER_COLORS[parseInt(clusterId) % CLUSTER_COLORS.length]}
                    shape="star"
                  />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div className="flex flex-wrap gap-4 mt-4 justify-center">
            {clusterDescriptions.map((desc) => (
              <div
                key={desc.cluster_id}
                className={`flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity px-3 py-1 rounded-full ${
                  selectedCluster === desc.cluster_id ? 'bg-slate-100 ring-2 ring-slate-300' : ''
                }`}
                onClick={() => setSelectedCluster(selectedCluster === desc.cluster_id ? null : desc.cluster_id)}
              >
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length] }}
                />
                <span className="text-sm text-slate-700">
                  Cluster {desc.cluster_id} ({desc.count} players)
                </span>
              </div>
            ))}
            {selectedCluster !== null && (
              <button
                className="text-sm text-blue-600 hover:text-blue-800 underline"
                onClick={() => setSelectedCluster(null)}
              >
                Clear Selection
              </button>
            )}
          </div>
        </div>

        {/* Cluster Statistics */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Cluster Distribution</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={clusterSizeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="cluster" />
                  <YAxis label={{ value: "Players", angle: -90, position: "insideLeft" }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3B82F6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Height by Cluster</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={clusterComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="cluster" />
                  <YAxis label={{ value: "Height (inches)", angle: -90, position: "insideLeft" }} />
                  <Tooltip />
                  <Bar dataKey="height" fill="#10B981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Selected Cluster Details */}
        {selectedCluster !== null && (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 mb-8 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Cluster {selectedCluster} Details</h2>
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-1">
                <h3 className="font-bold mb-3 text-slate-900">Statistics</h3>
                <div className="space-y-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Average Height</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_height.toFixed(1)}"
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Average Usage</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_usage.toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Rim Frequency</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_rim_freq.toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">3PT Attempt Rate</div>
                    <div className="text-2xl font-bold text-slate-900">
                      {clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_3pt_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Average BPM</div>
                    <div className={`text-2xl font-bold ${
                      (clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_bpm || 0) > 0
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}>
                      {clusterDescriptions.find((c) => c.cluster_id === selectedCluster)?.avg_bpm.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="col-span-2">
                <h3 className="font-bold mb-3 text-slate-900">Top 5 Players by BPM</h3>
                <div className="space-y-2">
                  {clusterDescriptions
                    .find((c) => c.cluster_id === selectedCluster)
                    ?.top_players.slice(0, 5)
                    .map((player, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between items-center bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors"
                      >
                        <div>
                          <div className="font-semibold text-slate-900">{player.Name}</div>
                          <div className="text-xs text-slate-500">{player.Team}</div>
                        </div>
                        <div className="text-lg font-bold text-slate-900">{player.BPM.toFixed(2)}</div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Team Cluster Composition */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Team Cluster Composition</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">Select Team</label>
              <select
                value={selectedTeam || ""}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              >
                {topTeams.map((team) => (
                  <option key={team.team} value={team.team}>
                    {team.team} ({team.total_players} players)
                  </option>
                ))}
              </select>
            </div>
            {selectedTeamData && (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={selectedTeamClusterData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${percent ? (percent * 100).toFixed(0) : 0}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {selectedTeamClusterData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CLUSTER_COLORS[index % CLUSTER_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-900">Cluster Radar Comparison</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={clusterComparisonData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="cluster" tick={{ fontSize: 10 }} />
                  <PolarRadiusAxis angle={90} domain={[-20, 10]} tick={{ fontSize: 8 }} />
                  <Radar
                    name="BPM"
                    dataKey="bpm"
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

        {/* Teams Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg p-6 border border-slate-200">
          <h2 className="text-xl font-bold mb-4 text-slate-900">Top 20 Teams by Clustered Players</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b-2 border-slate-200">
                  <th className="px-4 py-3 text-left font-semibold text-slate-900">Team</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-900">Total</th>
                  {[0, 1, 2, 3, 4, 5].map((clusterId) => (
                    <th key={clusterId} className="px-4 py-3 text-left font-semibold text-slate-900">
                      C{clusterId}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {topTeams.map((team) => (
                  <tr
                    key={team.team}
                    className={`border-b border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors ${
                      selectedTeam === team.team ? "bg-blue-50" : ""
                    }`}
                    onClick={() => setSelectedTeam(team.team)}
                  >
                    <td className="px-4 py-3 font-medium text-slate-900">{team.team}</td>
                    <td className="px-4 py-3 text-slate-600">{team.total_players}</td>
                    {[0, 1, 2, 3, 4, 5].map((clusterId) => (
                      <td key={clusterId} className="px-4 py-3 text-slate-600">
                        {team.clusters[clusterId] || 0}
                      </td>
                    ))}
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
