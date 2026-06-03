"use client";

/* @ts-nocheck - React Three Fiber JSX elements have type definition issues */

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";
import { fetchAllPlayers, fetchPlayerSimilar, fetchPrecomputedPositions, fetchNearestNeighbors } from "@/lib/api";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Float } from "@react-three/drei";

interface Player {
  AthleteSourceId: string;
  player_name: string;
  team: string;
  year?: string;
  adj_rapm_margin?: number;
  adj_rapm_offense?: number;
  adj_rapm_defense?: number;
  usage?: number;
  height?: number;
}

export default function SimilarityPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Player[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [similarPlayers, setSimilarPlayers] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [hoveredPlayer, setHoveredPlayer] = useState<Player | null>(null);
  const [cameraPosition, setCameraPosition] = useState<[number, number, number]>([0, 0, 150]);
  const [cameraTarget, setCameraTarget] = useState<[number, number, number]>([0, 0, 0]);
  const [positions, setPositions] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    // Fetch both in parallel for faster load
    Promise.all([fetchPlayers(), fetchPositions()]);
  }, []);

  // Search all players when query changes
  useEffect(() => {
    const searchAllPlayers = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        return;
      }
      
      setLoadingSearch(true);
      try {
        // Use the same search approach as advanced leaderboard
        const data = await fetchAllPlayers({ 
          limit: 20, 
          search: searchQuery, 
          dataTier: "enriched" 
        });
        setSearchResults(data);
      } catch (err) {
        console.error("Failed to search players:", err);
        setSearchResults([]);
      } finally {
        setLoadingSearch(false);
      }
    };

    const debounceTimer = setTimeout(searchAllPlayers, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);

  const fetchPositions = async () => {
    try {
      const data = await fetchPrecomputedPositions();
      setPositions(data.positions || []);
    } catch (err) {
      console.error("Failed to fetch positions:", err);
    }
  };

  const fetchPlayers = async () => {
    try {
      setLoading(true);
      // Fetch subset of enriched players for performance (default view)
      // @ts-ignore - dataTier parameter added to API function
      const data = await fetchAllPlayers({ limit: 500, sort: "adj_rapm_margin", order: "desc", dataTier: "enriched" });
      setPlayers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load players");
    } finally {
      setLoading(false);
    }
  };

  // Use precomputed positions from backend
  const playerPositions = useMemo(() => {
    if (players.length === 0 || positions.length === 0) return [];
    
    console.log(`Matching ${players.length} players to ${positions.length} positions`);
    
    // Debug: show sample IDs
    if (players.length > 0 && positions.length > 0) {
      console.log(`Sample player AthleteSourceId: ${players[0].AthleteSourceId}`);
      console.log(`Sample position ncaa_id: ${positions[0].ncaa_id}`);
    }
    
    // Match players to their positions (use latest year for each player)
    const result: { player: Player; position: [number, number, number] }[] = [];
    
    players.forEach(player => {
      // Try to find a position for this player (any year)
      const matchingPositions = positions.filter(p => p.ncaa_id === String(player.AthleteSourceId));
      
      if (matchingPositions.length > 0) {
        // Use the first matching position (or could prefer latest year)
        const pos = matchingPositions[0];
        result.push({
          player,
          position: [pos.x, pos.y, pos.z] as [number, number, number],
        });
      }
    });
    
    // Add selected player if not already in the result
    if (selectedPlayer) {
      const alreadyIncluded = result.some(r => r.player.AthleteSourceId === selectedPlayer.AthleteSourceId);
      if (!alreadyIncluded) {
        const selectedPos = positions.find(p => p.ncaa_id === String(selectedPlayer.AthleteSourceId));
        if (selectedPos) {
          result.push({
            player: selectedPlayer,
            position: [selectedPos.x, selectedPos.y, selectedPos.z] as [number, number, number],
          });
        }
      }
    }
    
    console.log(`Matched ${result.length} players to positions`);
    return result;
  }, [players, positions, selectedPlayer]);


  // Find nearest neighbors for selected player using 3D position distance
  const nearestNeighbors = useMemo(() => {
    if (!selectedPlayer || similarPlayers.length === 0) return [];
    
    return similarPlayers.map((sp) => {
      // Find position from the positions data (includes all players)
      const posData = positions.find(p => p.ncaa_id === String(sp.AthleteSourceId));
      
      if (posData) {
        return {
          position: [posData.x, posData.y, posData.z] as [number, number, number],
          distance: sp.distance || 0,
          similarity: sp.similarity || 0,
          year: sp.year,
          player: sp.player || null, // Use the full player data we fetched
          ncaa_id: sp.AthleteSourceId,
        };
      } else {
        return null;
      }
    }).filter((item): item is NonNullable<typeof item> => item !== null);
  }, [selectedPlayer, similarPlayers, positions]);

  const handlePlayerSelect = async (player: Player) => {
    setSelectedPlayer(player);
    setSearchQuery("");
    
    // Fetch nearest neighbors using 3D position distance
    setLoadingSimilar(true);
    try {
      console.log("Fetching nearest neighbors for:", player.AthleteSourceId);
      const neighborsData = await fetchNearestNeighbors(String(player.AthleteSourceId), 5);
      console.log("Nearest neighbors data:", neighborsData);
      
      // Convert neighbors to similar players format using positions CSV data
      const neighborPlayers = neighborsData.neighbors || [];
      
      const neighborsWithFullData = neighborPlayers.map((n: any) => {
        // Use data from positions CSV (has player_name and team)
        // Try to find enriched data from current players list for RAPM
        const enrichedPlayer = players.find(p => p.AthleteSourceId === n.ncaa_id);
        
        return {
          AthleteSourceId: n.ncaa_id,
          similarity: 1 - (n.distance / 10), // Convert distance to similarity score
          distance: n.distance,
          year: n.year,
          player: enrichedPlayer || { 
            AthleteSourceId: n.ncaa_id, 
            player_name: n.player_name || `Player ${n.ncaa_id}`, 
            team: n.team || 'N/A',
            adj_rapm_margin: null
          },
        };
      });
      
      setSimilarPlayers(neighborsWithFullData);
    } catch (err) {
      console.error("Failed to fetch nearest neighbors:", err);
      setSimilarPlayers([]);
    } finally {
      setLoadingSimilar(false);
    }
    
    // Find player position and zoom to it
    const playerPos = playerPositions.find(p => p.player.AthleteSourceId === player.AthleteSourceId);
    if (playerPos) {
      setCameraTarget(playerPos.position);
      setCameraPosition([
        playerPos.position[0] + 20,
        playerPos.position[1] + 20,
        playerPos.position[2] + 40
      ]);
    }
  };

  const handleResetView = () => {
    setSelectedPlayer(null);
    setSimilarPlayers([]);
    setCameraPosition([0, 0, 150]);
    setCameraTarget([0, 0, 0]);
  };

  console.log(`Page state: loading=${loading}, error=${error}, players=${players.length}, positions=${positions.length}, matched=${playerPositions.length}`);

  if (loading) {
    return (
      <ErrorBoundary>
        <div className="p-3 font-mono text-xs bg-[#E7E8D1] text-black min-h-screen">
          <div className="max-w-7xl mx-auto">
            <div className="border-b-2 border-black pb-4 mb-6">
              <h1 className="text-xs font-bold uppercase tracking-wide mb-2">Player Similarity Map</h1>
              <p className="text-xs text-black">Loading players... (Debug: {players.length} players, {positions.length} positions)</p>
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  if (error) {
    return (
      <ErrorBoundary>
        <div className="p-3 font-mono text-xs bg-[#E7E8D1] text-black min-h-screen">
          <ErrorMessage message={error} onRetry={fetchPlayers} />
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
            <h1 className="text-xs font-bold uppercase tracking-wide mb-2">Player Similarity Map</h1>
            <p className="text-xs text-black">
              3D visualization of all enriched players. Search for a player to zoom in and find similar players.
            </p>
          </div>

          {/* Search Panel */}
          <Panel>
            <PanelHeader>SEARCH PLAYER</PanelHeader>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name or team..."
                className="flex-1 border-2 border-black bg-[#E7E8D1] p-3 font-mono text-xs shadow-[3px_3px_0px_black] focus:outline-none focus:shadow-[3px_3px_0px_black]"
              />
              {selectedPlayer && (
                <button
                  onClick={handleResetView}
                  className="px-4 py-3 border-2 border-black bg-black text-white font-bold hover:bg-black/80 transition-all shadow-[3px_3px_0px_black]"
                >
                  RESET VIEW
                </button>
              )}
            </div>

            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="mt-2 border-2 border-black bg-[#E7E8D1] shadow-[3px_3px_0px_black] max-h-60 overflow-y-auto">
                {searchResults.map((player) => (
                  <div
                    key={player.AthleteSourceId}
                    onClick={() => handlePlayerSelect(player)}
                    className="p-3 border-b-2 border-black hover:bg-[#B8C0A8] cursor-pointer transition-all"
                  >
                    <div className="font-bold">{player.player_name}</div>
                    <div className="text-xs text-black">{player.team} • {player.year || 'N/A'} • RAPM: {player.adj_rapm_margin?.toFixed(2) || 'N/A'}</div>
                  </div>
                ))}
              </div>
            )}
          </Panel>

          {/* Selected Player Info */}
          {selectedPlayer && (
            <Panel>
              <PanelHeader>SELECTED PLAYER</PanelHeader>
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="border-2 border-black bg-[#E7E8D1] p-3 shadow-[3px_3px_0px_black]">
                  <div className="text-xs font-bold uppercase tracking-wide mb-1 text-black">Name</div>
                  <div className="text-xs font-bold">{selectedPlayer.player_name}</div>
                </div>
                <div className="border-2 border-black bg-[#E7E8D1] p-3 shadow-[3px_3px_0px_black]">
                  <div className="text-xs font-bold uppercase tracking-wide mb-1 text-black">Team</div>
                  <div className="text-xs font-bold">{selectedPlayer.team}</div>
                </div>
                <div className="border-2 border-black bg-[#E7E8D1] p-3 shadow-[3px_3px_0px_black]">
                  <div className="text-xs font-bold uppercase tracking-wide mb-1 text-black">RAPM</div>
                  <div className="text-xs font-bold">{selectedPlayer.adj_rapm_margin?.toFixed(2) || 'N/A'}</div>
                </div>
                <div className="border-2 border-black bg-[#E7E8D1] p-3 shadow-[3px_3px_0px_black]">
                  <div className="text-xs font-bold uppercase tracking-wide mb-1 text-black">Usage</div>
                  <div className="text-xs font-bold">{selectedPlayer.usage?.toFixed(1) || 'N/A'}%</div>
                </div>
              </div>

              {/* Nearest Neighbors */}
              <div className="border-2 border-black bg-[#E7E8D1] p-4 shadow-[3px_3px_0px_black]">
                <div className="border-b-2 border-black mb-3 pb-1 text-xs font-bold uppercase tracking-wide">
                  {loadingSimilar ? "Loading similar players..." : "Similar Players (from API)"}
                </div>
                <div className="space-y-2">
                  {nearestNeighbors.length === 0 && !loadingSimilar && (
                    <div className="text-xs text-black">No similar players found</div>
                  )}
                  {nearestNeighbors.map((item, i) => {
                    if (!item) return null;

                    return (
                      <div
                        key={item.ncaa_id}
                        className="flex items-center gap-3 p-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] transition-all shadow-[3px_3px_0px_black] cursor-pointer"
                        onClick={() => item.player?.player_name && router.push(`/player/${item.ncaa_id}`)}
                      >
                        <div className="w-8 h-8 border-2 border-black bg-[#E7E8D1] flex items-center justify-center font-bold text-xs">
                          {i + 1}
                        </div>
                        <div className="flex-1">
                          <div className="font-bold text-xs">{item.player?.player_name || `Player ${item.ncaa_id}`}</div>
                          <div className="text-xs text-black">{item.player?.team || 'N/A'}</div>
                        </div>
                        <div className="font-bold text-xs">
                          {item.year || 'N/A'}
                        </div>
                      </div>
                    );
                  }).filter(Boolean)}
                </div>
              </div>
            </Panel>
          )}

          {/* 3D Visualization */}
          <Panel>
            <PanelHeader>3D SIMILARITY MAP</PanelHeader>
            <div className="text-xs mb-2 text-black space-y-2">
              {selectedPlayer
                ? (
                  <>
                    <p>Viewing similar players to <strong>{selectedPlayer.player_name}</strong> (from similarity API). Similar players are found using cosine similarity on 11-dimensional feature vectors.</p>
                    <p><strong>How it works:</strong> Each player is represented by a vector combining 6 style stats (3PT Volume, Rim Pressure, Midrange, Playmaking, Off-Ball, Turnovers) and 5 impact stats (Scoring Impact, Assist Impact, Rebounding Impact, Defense Impact, Efficiency). Players with similar stat profiles cluster together in this 3D space.</p>
                    <p><strong>Dimensionality Reduction:</strong> UMAP (Uniform Manifold Approximation and Projection) reduces the 11-dimensional vectors to 3D for visualization while preserving local structure. Similar players appear close together, but 3D distance is an approximation—true similarity is calculated directly from the original vectors.</p>
                  </>
                )
                : (
                  <>
                    <p>Viewing enriched players positioned using UMAP on 11-dimensional style/impact vectors. Search for a player to find their most similar players.</p>
                    <p><strong>How it works:</strong> Each player is represented by a vector combining 6 style stats (3PT Volume, Rim Pressure, Midrange, Playmaking, Off-Ball, Turnovers) and 5 impact stats (Scoring Impact, Assist Impact, Rebounding Impact, Defense Impact, Efficiency). Players with similar stat profiles cluster together in this 3D space.</p>
                    <p><strong>Dimensionality Reduction:</strong> UMAP (Uniform Manifold Approximation and Projection) reduces the 11-dimensional vectors to 3D for visualization while preserving local structure. Similar players appear close together, but 3D distance is an approximation—true similarity is calculated directly from the original vectors.</p>
                  </>
                )
              }
            </div>
            <p className="text-xs mb-4 text-black font-mono">
              Debug: {players.length} players loaded, {positions.length} positions available, {playerPositions.length} matched
            </p>

            <div className="h-[700px] border-2 border-black bg-black relative overflow-hidden">
              {/* Player Tooltip */}
              {hoveredPlayer && (
                <div className="absolute top-4 left-4 border-2 border-black bg-[#C7D0B8] shadow-[3px_3px_0px_black] p-4 z-10 min-w-[200px]">
                  <div className="font-bold text-black text-xs mb-1">{hoveredPlayer.player_name}</div>
                  <div className="text-xs text-black mb-1">Team: {hoveredPlayer.team}</div>
                  <div className="text-xs text-black mb-1">RAPM: <span className={hoveredPlayer.adj_rapm_margin > 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>{hoveredPlayer.adj_rapm_margin?.toFixed(2) || 'N/A'}</span></div>
                </div>
              )}

              <Canvas camera={{ position: cameraPosition, fov: 60 }}>
                <OrbitControls 
                  enableZoom={true} 
                  enableRotate={true} 
                  autoRotate={false}
                  target={cameraTarget}
                />
                <ambientLight intensity={0.5} />
                <directionalLight position={[30, 30, 30]} intensity={1} color={0x3B82F6} />
                <directionalLight position={[-30, -30, -30]} intensity={0.5} color={0x8B5CF6} />

                {/* Render lines connecting selected player to neighbors */}
                {selectedPlayer && nearestNeighbors.length > 0 && (() => {
                  const selectedPos = positions.find(p => p.ncaa_id === String(selectedPlayer.AthleteSourceId));
                  if (!selectedPos) return null;
                  
                  return nearestNeighbors.map((n) => {
                    const neighborPos = positions.find(p => p.ncaa_id === String(n.ncaa_id));
                    if (!neighborPos) return null;
                    
                    const points = [
                      [selectedPos.x, selectedPos.y, selectedPos.z],
                      [neighborPos.x, neighborPos.y, neighborPos.z]
                    ] as [number, number, number][];
                    
                    return (
                      <Line
                        key={`line-${n.ncaa_id}`}
                        points={points}
                        color="#F59E0B"
                        opacity={0.3}
                        transparent
                        lineWidth={1}
                      />
                    );
                  });
                })()}

                {/* Render players - when selected, show only selected + neighbors; otherwise show default subset */}
                {(selectedPlayer ? [
                  // Add selected player
                  playerPositions.find(p => p.player.AthleteSourceId === selectedPlayer.AthleteSourceId),
                  // Add nearest neighbors
                  ...nearestNeighbors.map(n => {
                    const pos = positions.find(p => p.ncaa_id === String(n.ncaa_id));
                    if (pos) {
                      return {
                        position: [pos.x, pos.y, pos.z] as [number, number, number],
                        player: n.player || { AthleteSourceId: n.ncaa_id, player_name: pos.player_name, team: pos.team },
                      };
                    }
                    return null;
                  }).filter(Boolean)
                ].filter(Boolean) : playerPositions).map((item: any) => {
                  if (!item) return null;
                  
                  const isSelected = selectedPlayer?.AthleteSourceId === item.player.AthleteSourceId;
                  const isNeighbor = selectedPlayer && nearestNeighbors.some(n => n?.ncaa_id === item.player.AthleteSourceId);
                  
                  const isHovered = hoveredPlayer?.AthleteSourceId === item.player.AthleteSourceId;
                  let color;
                  if (isSelected) {
                    color = '#FFB3B3'; // Pastel red for selected
                  } else if (isNeighbor) {
                    color = '#FFD699'; // Pastel amber for similar players
                  } else {
                    // Pastel color based on player ID for variety
                    const hash = String(item.player.AthleteSourceId).split('').reduce((a: any, b: any) => ((a << 5) - a) + b.charCodeAt(0), 0);
                    const hue = Math.abs(hash) % 360;
                    color = `hsl(${hue}, 60%, 80%)`; // Pastel: high lightness, lower saturation
                  }
                  const scale = isSelected ? 1.2 : isNeighbor ? 1 : isHovered ? 1 : 0.7;

                  return (
                    <group key={item.player.AthleteSourceId} position={item.position}>
                      <group
                        onPointerOver={(e: any) => {
                          e.stopPropagation();
                          setHoveredPlayer(item.player);
                        }}
                        onPointerOut={() => setHoveredPlayer(null)}
                        onClick={() => item.player.player_name && handlePlayerSelect(item.player)}
                      >
                        <Float
                          speed={2}
                          rotationIntensity={0.2}
                          floatIntensity={0.5}
                        >
                          <mesh>
                            <sphereGeometry args={[scale, 12, 12]} />
                            <meshStandardMaterial 
                              color={color}
                              emissive={color}
                              emissiveIntensity={isHovered ? 0.6 : 0.3}
                              transparent
                              opacity={0.85}
                              metalness={0.3}
                              roughness={0.4}
                            />
                          </mesh>
                        </Float>
                      </group>
                    </group>
                  );
                })}
              </Canvas>
            </div>
          </Panel>
        </div>
      </div>
    </ErrorBoundary>
  );
}
