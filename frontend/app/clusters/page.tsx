"use client";

/* @ts-nocheck - React Three Fiber JSX elements have type definition issues */

import { useState, useEffect, useMemo } from "react";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { AnimatePresence } from "framer-motion";
import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

// Saturated color scheme for clusters (18 distinct vibrant colors for better differentiation)
const CLUSTER_COLORS = [
  "#FF6B6B", // Red
  "#4ECDC4", // Teal
  "#9B59B6", // Purple
  "#2ECC71", // Green
  "#3498DB", // Blue
  "#F39C12", // Orange
  "#E74C3C", // Coral
  "#1ABC9C", // Turquoise
  "#8E44AD", // Violet
  "#27AE60", // Emerald
  "#2980B9", // Navy
  "#E67E22", // Carrot
  "#C0392B", // Dark red
  "#16A085", // Dark teal
  "#6C3483", // Dark purple
  "#1D8348", // Dark green
  "#2471A3", // Dark blue
  "#D35400", // Pumpkin
];

interface ClusterDescription {
  cluster_id: number;
  count: number;
  avg_height: number;
  avg_usage: number;
  avg_rim_freq: number;
  avg_3pt_pct: number;
  avg_bpm: number;
  avg_obpm?: number;
  avg_dbpm?: number;
  avg_def_rating?: number;
  name?: string;
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
  AthleteSourceId?: string;
}

export default function ClusterAnalysis() {
  const [clusterDescriptions, setClusterDescriptions] = useState<ClusterDescription[]>([]);
  const [clusterPlayers, setClusterPlayers] = useState<ClusterPlayer[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [hoveredPlayer, setHoveredPlayer] = useState<ClusterPlayer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [descriptionsRes, playersRes] = await Promise.all([
        fetch("/api/v1/clusters/descriptions"),
        fetch("/api/v1/clusters/players"),
      ]);

      if (!descriptionsRes.ok || !playersRes.ok) {
        throw new Error("Failed to fetch cluster data");
      }

      const descriptionsData = await descriptionsRes.json();
      const playersData = await playersRes.json();

      setClusterDescriptions(descriptionsData);
      setClusterPlayers(playersData);
      
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

  const handleClusterClick = (clusterId: number) => {
    if (selectedCluster === clusterId) {
      // Toggle back to full view
      setSelectedCluster(null);
    } else {
      // Select cluster
      setSelectedCluster(clusterId);
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

  // Get top 30 players per cluster by BPM and calculate solar system positions
  const solarSystemData = useMemo(() => {
    const result: Record<number, { center: ClusterPlayer; orbiters: ClusterPlayer[]; systemPosition: [number, number, number] }> = {};
    
    // Arrange cluster systems in concentric orbits around center
    const numClusters = clusterDescriptions.length;
    const orbits = Math.ceil(Math.sqrt(numClusters)); // Number of orbital rings
    
    clusterDescriptions.forEach((desc, idx) => {
      const clusterPlayersData = clusterPlayers
        .filter((p) => p.cluster === desc.cluster_id)
        .sort((a, b) => (b.BPM || 0) - (a.BPM || 0))
        .slice(0, 30);
      
      if (clusterPlayersData.length === 0) return;
      
      const centerPlayer = clusterPlayersData[0]; // Best player as planet
      const orbiters = clusterPlayersData.slice(1); // Rest as orbiting stars
      
      // Calculate orbital position for this cluster system
      const orbitRing = Math.floor(idx / orbits); // Which orbital ring
      const positionInRing = idx % orbits; // Position within the ring
      
      const orbitRadius = 12 + orbitRing * 10; // More compact for better 3D balance
      const angle = (positionInRing / orbits) * Math.PI * 2 + (orbitRing * 0.5); // Offset angle for each ring
      
      const systemPosition: [number, number, number] = [
        Math.cos(angle) * orbitRadius,
        Math.sin(angle) * orbitRadius,
        (orbitRing - orbits / 2) * 12 // Balanced Z variation
      ];
      
      result[desc.cluster_id] = {
        center: centerPlayer,
        orbiters,
        systemPosition
      };
    });
    
    return result;
  }, [clusterPlayers, clusterDescriptions]);

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


  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-8 font-mono text-xs bg-[#E7E8D1] text-black min-h-screen">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <div className="h-12 w-64 bg-[#C7D0B8] border-2 border-black animate-pulse mb-2" />
              <div className="h-6 w-96 bg-[#C7D0B8] border-2 border-black animate-pulse" />
            </div>
            <div className="grid grid-cols-4 gap-6 mb-8">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-[#C7D0B8] border-2 border-black shadow-[3px_3px_0px_black] p-6">
                  <div className="h-4 w-24 bg-[#B8C0A8] border-2 border-black animate-pulse mb-2" />
                  <div className="h-8 w-16 bg-[#B8C0A8] border-2 border-black animate-pulse" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-[#C7D0B8] border-2 border-black shadow-[3px_3px_0px_black] p-5">
                  <div className="h-4 w-32 bg-[#B8C0A8] border-2 border-black animate-pulse mb-3" />
                  <div className="space-y-2">
                    {[1, 2, 3, 4, 5].map((j) => (
                      <div key={j} className="h-3 bg-[#B8C0A8] border-2 border-black animate-pulse" />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  if (error) {
    return (
      <ErrorBoundary>
        <div className="p-6 font-mono text-xs bg-[#E7E8D1] text-black">
          <ErrorMessage message={error} onRetry={fetchData} />
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <div className="p-3 font-mono text-xs bg-[#E7E8D1] text-black min-h-screen">
        <div className="max-w-7xl mx-auto space-y-6">
        {/* Title */}
        <div className="border-b-2 border-black pb-4">
          <h1 className="text-xs font-bold uppercase tracking-wide mb-2">Cluster Analysis</h1>
          <p className="text-xs text-black">
            Explore player playstyle clusters and their characteristics
          </p>
        </div>

        {/* Key Insights */}
        <Panel>
          <PanelHeader>KEY INSIGHTS</PanelHeader>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: "Total Players", value: clusterPlayers.length },
              { label: "Clusters", value: clusterDescriptions.length },
              { label: "Playstyle Features", value: 18 },
              { label: "Avg BPM Range", value: "-6 to +5" },
            ].map((stat, i) => (
              <div key={i} className="border-2 border-black bg-[#E7E8D1] p-4 shadow-[3px_3px_0px_black]">
                <div className="text-xs font-bold uppercase tracking-wide mb-2 text-black">{stat.label}</div>
                <div className="text-xs font-bold">{stat.value}</div>
              </div>
            ))}
          </div>
        </Panel>

        {/* Cluster Selector Dropdown */}
        <Panel>
          <PanelHeader>SELECT CLUSTER</PanelHeader>
          <div className="flex items-center gap-4">
            <select
              value={selectedCluster || ''}
              onChange={(e) => handleClusterClick(parseInt(e.target.value))}
              className="flex-1 border-2 border-black bg-[#E7E8D1] p-3 font-mono text-xs shadow-[3px_3px_0px_black] focus:outline-none focus:shadow-[3px_3px_0px_black]"
            >
              <option value="">-- Select a Cluster --</option>
              {clusterDescriptions
                .sort((a, b) => a.cluster_id - b.cluster_id)
                .map((desc) => (
                  <option key={desc.cluster_id} value={desc.cluster_id}>
                    Cluster {desc.cluster_id}: {desc.name || 'Unnamed'} ({desc.count} players)
                  </option>
                ))}
            </select>
            {selectedCluster !== null && (
              <button
                onClick={() => handleClusterClick(selectedCluster)}
                className="px-4 py-3 border-2 border-black bg-black text-white font-bold hover:bg-black/80 transition-all shadow-[3px_3px_0px_black]"
              >
                CLEAR
              </button>
            )}
          </div>
        </Panel>

        {/* 3D Solar System */}
        <Panel>
          <PanelHeader>3D PLAYSTYLE SIMILARITY MAP</PanelHeader>
          <p className="text-xs mb-4 text-black">
            Interactive 3D visualization of top 30 players per cluster. Select a cluster from the dropdown to view its system. Drag to rotate, scroll to zoom.
          </p>

          {selectedCluster !== null && (
            <button
              onClick={() => setSelectedCluster(null)}
              className="mb-4 px-4 py-2 border-2 border-black bg-black text-white text-xs font-bold hover:bg-black/80 transition-all shadow-[3px_3px_0px_black]"
            >
              FULL VIEW
            </button>
          )}

          <div className="h-[700px] border-2 border-black bg-black relative overflow-hidden">
            {/* Player Tooltip */}
            {hoveredPlayer && (
              <div className="absolute top-4 left-4 border-2 border-black bg-[#C7D0B8] shadow-[3px_3px_0px_black] p-4 z-10 min-w-[200px]">
                <div className="font-bold text-black text-xs mb-1">{hoveredPlayer.Name}</div>
                <div className="text-xs text-black mb-1">Team: {hoveredPlayer.Team}</div>
                <div className="text-xs text-black mb-1">BPM: <span className={hoveredPlayer.BPM > 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>{hoveredPlayer.BPM?.toFixed(2) || 'N/A'}</span></div>
                <div className="text-xs text-black">Cluster: {hoveredPlayer.cluster}</div>
              </div>
            )}
            
            <Canvas camera={{ position: [40, 40, 80], fov: 60 }}>
              <OrbitControls 
                enableZoom={true} 
                enableRotate={true} 
                autoRotate={false}
                target={[0, 0, 0]}
              />
              <ambientLight intensity={0.5} />
              <directionalLight position={[30, 30, 30]} intensity={1} color={0x3B82F6} />
              <directionalLight position={[-30, -30, -30]} intensity={0.5} color={0x8B5CF6} />
              
              {/* Solar system visualization - show selected cluster or all */}
              {clusterDescriptions
                .filter((desc) => selectedCluster === null || desc.cluster_id === selectedCluster)
                .map((desc) => {
                  const systemData = solarSystemData[desc.cluster_id];
                  if (!systemData) return null;
                  
                  const [sx, sy, sz] = systemData.systemPosition;
                  
                  return (
                    <group key={`system-${desc.cluster_id}`} position={[sx, sy, sz]}>
                    {/* Central planet (best player) */}
                    <group
                      onPointerOver={(e: any) => {
                        e.stopPropagation();
                        setHoveredPlayer(systemData.center);
                      }}
                      onPointerOut={() => setHoveredPlayer(null)}
                    >
                      <mesh>
                        <sphereGeometry args={[3, 32, 32]} />
                        <meshStandardMaterial 
                          color={CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length]}
                          emissive={CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length]}
                          emissiveIntensity={0.6}
                          transparent
                          opacity={0.95}
                          metalness={0.5}
                          roughness={0.2}
                        />
                      </mesh>
                    </group>
                    
                    {/* Orbiting stars (other players) */}
                    {systemData.orbiters.map((player, i) => {
                      const angle = (i / systemData.orbiters.length) * Math.PI * 2;
                      const orbitRadius = 6 + (i % 3) * 2; // Varying orbit radii
                      const x = Math.cos(angle) * orbitRadius;
                      const y = Math.sin(angle) * orbitRadius;
                      const z = (i % 2 - 0.5) * 3; // Slight Z variation
                      
                      const isHovered = hoveredPlayer?.Name === player.Name;
                      
                      return (
                        <group 
                          key={i}
                          position={[x, y, z]}
                          scale={isHovered ? 1.5 : 1}
                        >
                          <mesh
                            onPointerOver={(e: any) => {
                              e.stopPropagation();
                              setHoveredPlayer(player);
                            }}
                            onPointerOut={() => setHoveredPlayer(null)}
                          >
                            <sphereGeometry args={[0.5, 16, 16]} />
                            <meshStandardMaterial 
                              color={CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length]}
                              emissive={CLUSTER_COLORS[desc.cluster_id % CLUSTER_COLORS.length]}
                              emissiveIntensity={isHovered ? 0.8 : 0.4}
                              transparent
                              opacity={0.9}
                              metalness={0.3}
                              roughness={0.3}
                            />
                          </mesh>
                        </group>
                      );
                    })}
                  </group>
                );
              })}
            </Canvas>
          </div>
        </Panel>

        {/* Cluster Statistics */}
        <Panel>
          <PanelHeader>CLUSTER STATISTICS</PanelHeader>
          <div className="grid grid-cols-2 gap-4">
            <div className="border-2 border-black bg-[#E7E8D1] p-4">
              <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                Cluster Distribution
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clusterSizeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="black" />
                    <XAxis dataKey="cluster" tick={{ fontSize: 10, fill: 'black' }} />
                    <YAxis tick={{ fontSize: 10, fill: 'black' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#C7D0B8',
                        border: '2px solid black',
                        boxShadow: '3px 3px 0px black'
                      }}
                    />
                    <Bar dataKey="count" fill="black" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="border-2 border-black bg-[#E7E8D1] p-4">
              <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                Height by Cluster
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clusterComparisonData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="black" />
                    <XAxis dataKey="cluster" tick={{ fontSize: 10, fill: 'black' }} />
                    <YAxis tick={{ fontSize: 10, fill: 'black' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#C7D0B8',
                        border: '2px solid black',
                        boxShadow: '3px 3px 0px black'
                      }}
                    />
                    <Bar dataKey="height" fill="black" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </Panel>

        {/* Selected Cluster Details */}
        <AnimatePresence>
          {selectedCluster !== null && (
            <Panel>
              <PanelHeader>CLUSTER {selectedCluster} DETAILS</PanelHeader>
              {(() => {
                const desc = clusterDescriptions.find((c) => c.cluster_id === selectedCluster);
                if (!desc) return null;
                return (
                  <>
                    <div className="border-b-2 border-black pb-3 mb-4">
                      <h3 className="text-xs font-bold mb-1 uppercase tracking-wide">{desc.name || 'Unnamed Cluster'}</h3>
                      <p className="text-xs text-black">{desc.count} players in this cluster</p>
                    </div>

                    {/* Key Statistics */}
                    <div className="grid grid-cols-4 gap-3 mb-4">
                      {[
                        { label: "Players", value: desc.count },
                        { label: "Avg Height", value: `${desc.avg_height.toFixed(1)}` },
                        { label: "Avg Usage", value: `${desc.avg_usage.toFixed(1)}%` },
                        { label: "Avg BPM", value: desc.avg_bpm.toFixed(1) },
                      ].map((stat, i) => (
                        <div key={i} className="border-2 border-black bg-[#E7E8D1] p-3 shadow-[3px_3px_0px_black]">
                          <div className="text-xs font-bold uppercase tracking-wide mb-1 text-black">{stat.label}</div>
                          <div className="text-xs font-bold">{stat.value}</div>
                        </div>
                      ))}
                    </div>

                    {/* Detailed Statistics */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="border-2 border-black bg-[#E7E8D1] p-4 shadow-[3px_3px_0px_black]">
                        <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                          Offensive Profile
                        </div>
                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-black">3PT Attempt Rate:</span>
                            <span className="font-bold">{desc.avg_3pt_pct.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-black">Rim Frequency:</span>
                            <span className="font-bold">{desc.avg_rim_freq.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-black">OBPM:</span>
                            <span className={`font-bold ${(desc.avg_obpm || 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>{desc.avg_obpm?.toFixed(2) || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                      <div className="border-2 border-black bg-[#E7E8D1] p-4 shadow-[3px_3px_0px_black]">
                        <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                          Defensive Profile
                        </div>
                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-black">DBPM:</span>
                            <span className={`font-bold ${(desc.avg_dbpm || 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>{desc.avg_dbpm?.toFixed(2) || 'N/A'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-black">Defensive Rating:</span>
                            <span className="font-bold">{desc.avg_def_rating?.toFixed(1) || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Top 5 Players */}
                    <div className="border-2 border-black bg-[#E7E8D1] p-4 shadow-[3px_3px_0px_black]">
                      <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                        Top 5 Players by BPM
                      </div>
                      <div className="space-y-2">
                        {selectedClusterPlayers
                          .sort((a, b) => (b.BPM || 0) - (a.BPM || 0))
                          .slice(0, 5)
                          .map((player, i) => (
                            <a
                              key={player.Name}
                              href={`/player/${player.Name.toLowerCase().replace(/\s+/g, '-')}`}
                              className="flex items-center gap-3 p-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] transition-all shadow-[3px_3px_0px_black]"
                            >
                              <div className="w-8 h-8 border-2 border-black bg-[#E7E8D1] flex items-center justify-center font-bold text-xs">
                                {i + 1}
                              </div>
                              <div className="flex-1">
                                <div className="font-bold text-xs">{player.Name}</div>
                                <div className="text-xs text-black">{player.Team}</div>
                              </div>
                              <div className="font-bold text-xs">
                                {player.BPM > 0 ? (
                                  <span className="text-green-600">+{player.BPM?.toFixed(1)}</span>
                                ) : (
                                  <span className="text-red-600">{player.BPM?.toFixed(1)}</span>
                                )}
                              </div>
                            </a>
                          ))}
                      </div>
                    </div>
                  </>
                );
              })()}
            </Panel>
          )}
        </AnimatePresence>
        </div>
      </div>
    </ErrorBoundary>
  );
}
