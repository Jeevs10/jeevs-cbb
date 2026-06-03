"use client";

import { useState, useEffect, useRef } from "react";
import { TEAM_COLORS } from "./teamColors";

interface Player {
  id?: string | number;
  AthleteSourceId?: string | number;
  name?: string;
  player_name?: string;
  team?: string | string[];
  teams?: string[];
  year?: number | number[];
  years?: number[];
  Position?: string;
  roster_height?: string | number;
  hometown?: string;
  conf?: string;
}

// Helper functions to handle both API formats
const getPlayerId = (player: Player): string => String(player.id || player.AthleteSourceId || '');
const getPlayerName = (player: Player): string => player.player_name || player.name || 'Unknown';
const getPlayerTeams = (player: Player): string[] => {
  if (player.teams) return Array.isArray(player.teams) ? player.teams : [player.teams];
  if (player.team) return Array.isArray(player.team) ? player.team : [player.team];
  return [];
};
const getPlayerYears = (player: Player): number[] => {
  if (player.years) return Array.isArray(player.years) ? player.years : [player.years];
  if (player.year) return Array.isArray(player.year) ? player.year : [player.year];
  return [];
};

const getTeamColor = (team: string): { primary: string; secondary: string } => {
  if (!team) return { primary: "#FFD700", secondary: "#FFA500" };
  // Try exact match first
  if (TEAM_COLORS[team]) return TEAM_COLORS[team];
  // Try partial match
  for (const [key, value] of Object.entries(TEAM_COLORS)) {
    if (team.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(team.toLowerCase())) {
      return value;
    }
  }
  // Default gold color
  return { primary: "#FFD700", secondary: "#FFA500" };
};

interface GamePair {
  start_player: Player;
  end_player: Player;
  distance: number;
}

export default function GamePage() {
  const [gamePair, setGamePair] = useState<GamePair | null>(null);
  const [playerChain, setPlayerChain] = useState<Player[]>([]);
  const [currentInput, setCurrentInput] = useState("");
  const [gameStarted, setGameStarted] = useState(false);
  const [gameEnded, setGameEnded] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [shortestPath, setShortestPath] = useState<Player[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<Player[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [shake, setShake] = useState(false);
  const [newNodeIndex, setNewNodeIndex] = useState<number | null>(null);
  const [flippedCards, setFlippedCards] = useState<Set<string | number>>(new Set());

  const toggleCardFlip = (index: string | number) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };
  
  // Filter states
  const [selectedConferences, setSelectedConferences] = useState<string[]>([]);
  const [selectedYears, setSelectedYears] = useState<number[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [targetDistance, setTargetDistance] = useState(6);
  
  // Available conferences and years
  const [availableConferences, setAvailableConferences] = useState<string[]>([]);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Fetch available conferences and years
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        // Fetch available years
        const yearsRes = await fetch("http://localhost:8000/api/v1/years");
        const yearsData = await yearsRes.json();
        setAvailableYears(yearsData.years || [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]);
        
        // Set common conferences (can be expanded or fetched from API)
        setAvailableConferences([
          "ACC", "Big 12", "Big East", "Big Ten", "Pac-12", "SEC",
          "AAC", "Atlantic 10", "Mountain West", "WCC"
        ]);
      } catch (err) {
        console.error("Failed to fetch filters:", err);
        setAvailableYears([2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]);
        setAvailableConferences(["ACC", "Big 12", "Big East", "Big Ten", "Pac-12", "SEC"]);
      }
    };
    fetchFilters();
  }, []);

  // Reload graph with filters
  const reloadGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/game/reload-graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conferences: selectedConferences.length > 0 ? selectedConferences : null,
          years: selectedYears.length > 0 ? selectedYears : null
        }),
      });
      if (!res.ok) throw new Error("Failed to reload graph");
      const data = await res.json();
      console.log("Graph reloaded:", data);
      // Fetch new game pair after reload
      fetchGamePair();
    } catch (err) {
      console.error("Failed to reload graph:", err);
      setError("Failed to apply filters");
    } finally {
      setLoading(false);
    }
  };

  // Fetch random game pair
  const fetchGamePair = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/game/random-pair?min_distance=${targetDistance}&max_distance=${targetDistance}`);
      if (!res.ok) throw new Error("Failed to fetch game pair");
      const data = await res.json();
      setGamePair(data);
      setPlayerChain([data.start_player]);
      setGameStarted(false);
      setGameEnded(false);
      setTimeElapsed(0);
      setShortestPath(null);
      setCurrentInput("");
      setNewNodeIndex(null);
    } catch (err) {
      setError("Failed to start game. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Start game timer
  const startGame = () => {
    setGameStarted(true);
    timerRef.current = setInterval(() => {
      setTimeElapsed((prev) => prev + 1);
    }, 1000);
  };

  // Give up and show shortest path
  const giveUp = async () => {
    if (!gamePair) return;
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    setGameEnded(true);
    setGameStarted(false);

    try {
      const res = await fetch("http://localhost:8000/api/v1/game/shortest-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_id1: getPlayerId(gamePair.start_player),
          player_id2: getPlayerId(gamePair.end_player),
        }),
      });
      if (!res.ok) throw new Error("Failed to fetch shortest path");
      const data = await res.json();
      setShortestPath(data.path);
    } catch (err) {
      console.error("Failed to fetch shortest path:", err);
    }
  };

  // Search for players
  const searchPlayers = async (query: string) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/api/v1/players?search=${query}&limit=50`);
      if (!res.ok) throw new Error("Failed to search players");
      const data = await res.json();
      const results = data.results || [];
      
      // Deduplicate by player ID to avoid showing multiple versions of the same player
      // But keep different players with the same name (different IDs)
      const uniqueResults = results.filter((player, index, self) => {
        const playerId = getPlayerId(player);
        const firstIndex = self.findIndex(p => getPlayerId(p) === playerId);
        return index === firstIndex;
      });
      
      setSearchResults(uniqueResults);
      setShowSearchResults(true);
    } catch (err) {
      console.error("Failed to search players:", err);
    }
  };

  // Handle player selection
  const selectPlayer = (player: Player) => {
    if (!gamePair || !gameStarted) return;

    const currentLastPlayer = playerChain[playerChain.length - 1];
    
    // Check if selected player is a teammate of current player
    fetch("http://localhost:8000/api/v1/game/check-teammates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        player_id1: getPlayerId(currentLastPlayer),
        player_id2: getPlayerId(player),
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.are_teammates) {
          const newIndex = playerChain.length;
          // Fetch full player info from graph to ensure we have teams/years arrays
          fetch(`http://localhost:8000/api/v1/game/player/${getPlayerId(player)}`)
            .then(res => res.json())
            .then(playerData => {
              setPlayerChain([...playerChain, playerData]);
              setCurrentInput("");
              setShowSearchResults(false);
              setSearchResults([]);
              setNewNodeIndex(newIndex);
              
              // Remove animation after it plays
              setTimeout(() => setNewNodeIndex(null), 500);

              // Check if reached end player
              if (getPlayerId(playerData) === getPlayerId(gamePair.end_player)) {
                if (timerRef.current) {
                  clearInterval(timerRef.current);
                }
                setGameEnded(true);
                setGameStarted(false);
              }
            })
            .catch(() => {
              // Fallback to using the player as-is if fetch fails
              setPlayerChain([...playerChain, player]);
              setCurrentInput("");
              setShowSearchResults(false);
              setSearchResults([]);
              setNewNodeIndex(newIndex);
              
              setTimeout(() => setNewNodeIndex(null), 500);

              if (getPlayerId(player) === getPlayerId(gamePair.end_player)) {
                if (timerRef.current) {
                  clearInterval(timerRef.current);
                }
                setGameEnded(true);
                setGameStarted(false);
              }
            });
        } else {
          setError(`${getPlayerName(player)} was not a teammate of ${getPlayerName(currentLastPlayer)}`);
          setShake(true);
          setTimeout(() => setShake(false), 500);
        }
      })
      .catch((err) => {
        console.error("Failed to check teammates:", err);
        setError("Failed to check teammate connection");
      });
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCurrentInput(value);
    setError(null); // Clear error when user starts typing
    if (gameStarted) {
      searchPlayers(value);
    }
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Load game pair on mount
  useEffect(() => {
    fetchGamePair();
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Handle click outside search results
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchInputRef.current && !searchInputRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#E7E8D1] p-4 font-mono text-xs">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-xs font-bold uppercase tracking-wide">CBB Wikirace</h1>
          <button
            onClick={fetchGamePair}
            className="px-4 py-2 bg-black text-white font-bold border-2 border-black hover:bg-gray-800 shadow-[3px_3px_0px_black]"
          >
            Refresh
          </button>
        </div>
        <p className="mb-4 text-black">
          Connect the starting player to the ending player by entering players who were teammates.
        </p>

        {/* Filters Section */}
        <div className="bg-[#E7E8D1] border-2 border-black p-4 mb-4 shadow-[3px_3px_0px_black]">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="w-full flex justify-between items-center font-bold mb-2 uppercase tracking-wide"
          >
            <span>Filters</span>
            <span>{showFilters ? '▼' : '▶'}</span>
          </button>
          
          {showFilters && (
            <div className="space-y-4">
              {/* Conference Filter */}
              <div>
                <div className="font-bold mb-2 uppercase tracking-wide">Conferences:</div>
                <div className="flex flex-wrap gap-2">
                  {availableConferences.map(conf => (
                    <button
                      key={conf}
                      onClick={() => {
                        setSelectedConferences(prev =>
                          prev.includes(conf)
                            ? prev.filter(c => c !== conf)
                            : [...prev, conf]
                        );
                      }}
                      className={`px-3 py-1 text-xs border-2 border-black ${
                        selectedConferences.includes(conf)
                          ? 'bg-black text-white'
                          : 'bg-[#E7E8D1]'
                      }`}
                    >
                      {conf}
                    </button>
                  ))}
                </div>
              </div>

              {/* Year Filter */}
              <div>
                <div className="font-bold mb-2 uppercase tracking-wide">Years:</div>
                <div className="flex flex-wrap gap-2">
                  {availableYears.map(year => (
                    <button
                      key={year}
                      onClick={() => {
                        setSelectedYears(prev =>
                          prev.includes(year)
                            ? prev.filter(y => y !== year)
                            : [...prev, year]
                        );
                      }}
                      className={`px-3 py-1 text-xs border-2 border-black ${
                        selectedYears.includes(year)
                          ? 'bg-black text-white'
                          : 'bg-[#E7E8D1]'
                      }`}
                    >
                      {year}
                    </button>
                  ))}
                </div>
              </div>

              {/* Difficulty Filter */}
              <div>
                <div className="font-bold mb-2 uppercase tracking-wide">Target Distance:</div>
                <div className="flex flex-wrap gap-2">
                  {[3, 4, 5, 6, 7, 8].map(distance => (
                    <button
                      key={distance}
                      onClick={() => setTargetDistance(distance)}
                      className={`px-3 py-1 text-xs border-2 border-black ${
                        targetDistance === distance
                          ? 'bg-black text-white'
                          : 'bg-[#E7E8D1]'
                      }`}
                    >
                      {distance}
                    </button>
                  ))}
                </div>
                <div className="text-xs text-black mt-1">
                  Exact shortest path length
                </div>
              </div>

              {/* Apply Filters Button */}
              <button
                onClick={reloadGraph}
                disabled={loading}
                className="w-full bg-[#C7D0B8] border-2 border-black py-2 font-bold hover:bg-[#B8C0A8] disabled:opacity-50 shadow-[3px_3px_0px_black]"
              >
                {loading ? 'Applying Filters...' : 'Apply Filters & Reload'}
              </button>

              {/* Clear Filters Button */}
              {(selectedConferences.length > 0 || selectedYears.length > 0) && (
                <button
                  onClick={() => {
                    setSelectedConferences([]);
                    setSelectedYears([]);
                    reloadGraph();
                  }}
                  className="w-full bg-[#E7E8D1] border-2 border-black py-2 font-bold hover:bg-[#B8C0A8] shadow-[3px_3px_0px_black]"
                >
                  Clear All Filters
                </button>
              )}
            </div>
          )}
        </div>

        {loading && !gamePair && (
          <div className="text-center py-8">Loading game...</div>
        )}

        {error && !gamePair && (
          <div className="bg-[#E7E8D1] border-2 border-black p-4 mb-4 shadow-[3px_3px_0px_black]">
            {error}
            <button
              onClick={fetchGamePair}
              className="ml-4 px-2 py-1 bg-black text-white border-2 border-black shadow-[3px_3px_0px_black]"
            >
              Retry
            </button>
          </div>
        )}

        {gamePair && (
          <div className="space-y-4">
            {/* Game Status Bar */}
            <div className="bg-[#C7D0B8] border-2 border-black p-3 flex justify-between items-center shadow-[3px_3px_0px_black]">
              <div className="font-bold uppercase tracking-wide">Target Distance: {gamePair.distance}</div>
              <div className="font-bold uppercase tracking-wide">Time: {formatTime(timeElapsed)}</div>
            </div>

            {/* Controls */}
            {!gameStarted && !gameEnded && (
              <button
                onClick={startGame}
                className="w-full bg-black text-white py-3 font-bold border-2 border-black hover:bg-gray-800 shadow-[3px_3px_0px_black]"
              >
                Start Game
              </button>
            )}

            {gameStarted && (
              <button
                onClick={giveUp}
                className="w-full bg-red-600 text-white py-3 font-bold border-2 border-black hover:bg-red-700 shadow-[3px_3px_0px_black]"
              >
                Give Up
              </button>
            )}

            {gameEnded && (
              <button
                onClick={fetchGamePair}
                className="w-full bg-black text-white py-3 font-bold border-2 border-black hover:bg-gray-800 shadow-[3px_3px_0px_black]"
              >
                New Game
              </button>
            )}

            {/* Player Chain Visualization with Collectible Cards */}
            <div className="bg-[#E7E8D1] border-2 border-black p-6 shadow-[3px_3px_0px_black]">
              <h2 className="font-bold mb-4 text-center uppercase tracking-wide">Your Path:</h2>
              <div className="flex flex-wrap justify-center items-center gap-4">
                {playerChain.map((player, index) => (
                  <div key={getPlayerId(player)} className="flex items-center gap-4">
                    {/* Collectible Card */}
                    <div
                      className={`
                        relative group cursor-pointer card-flip-container
                        ${shake && index === playerChain.length - 1 ? 'animate-shake' : ''}
                        ${newNodeIndex === index ? 'animate-pop' : ''}
                        transition-all duration-300
                      `}
                      style={{
                        width: '144px',
                        height: '192px'
                      }}
                      onClick={() => toggleCardFlip(index)}
                    >
                      <div className={`card-flip-inner ${flippedCards.has(index) ? 'flipped' : ''}`}>
                        {/* Front of card */}
                        <div
                          className="card-flip-front relative w-36 h-48 border-2 border-black shadow-[3px_3px_0px_black] hover:shadow-[3px_3px_0px_black] transition-all duration-300 overflow-hidden bg-[#E7E8D1]"
                        >
                          {/* Card header with team primary color */}
                          <div
                            className="text-white p-2 text-center"
                            style={{
                              backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').primary
                            }}
                          >
                            <div className="text-xs font-bold tracking-wider truncate uppercase">
                              {getPlayerTeams(player)[0] || 'Unknown'}
                            </div>
                          </div>

                          {/* Player info */}
                          <div className="p-3 flex flex-col items-center text-center bg-[#E7E8D1]">
                            {/* Player name */}
                            <div className="font-bold text-xs text-black mb-1 line-clamp-2 leading-tight">
                              {getPlayerName(player)}
                            </div>

                            {/* Position */}
                            {player.Position && (
                              <div className="text-xs text-black font-bold mb-1">
                                {player.Position}
                              </div>
                            )}

                            {/* Team */}
                            {getPlayerTeams(player).length > 0 && (
                              <div className="text-xs text-black font-medium mb-1 truncate">
                                {getPlayerTeams(player)[0]}
                              </div>
                            )}

                            {/* Year */}
                            {getPlayerYears(player).length > 0 && (
                              <div className="text-xs text-black font-bold">
                                {getPlayerYears(player)[0]}
                              </div>
                            )}

                            <div className="text-xs text-black mt-2 italic">
                              Click for more info
                            </div>
                          </div>

                          {/* Card footer with team secondary color */}
                          <div
                            className="absolute bottom-0 left-0 right-0 h-2"
                            style={{
                              backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').secondary
                            }}
                          ></div>

                          {/* Step number badge */}
                          <div className="absolute -top-2 -right-2 w-7 h-7 bg-black text-white text-xs font-bold flex items-center justify-center border-2 border-white shadow-[3px_3px_0px_black]">
                            {index + 1}
                          </div>
                        </div>

                        {/* Back of card */}
                        <div
                          className="card-flip-back relative w-36 h-48 border-2 border-black shadow-[3px_3px_0px_black] overflow-hidden bg-[#E7E8D1]"
                        >
                          {/* Card header with team primary color */}
                          <div
                            className="text-white p-2 text-center"
                            style={{
                              backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').primary
                            }}
                          >
                            <div className="text-xs font-bold tracking-wider truncate uppercase">
                              {getPlayerName(player)}
                            </div>
                          </div>

                          {/* Player details */}
                          <div className="p-3 flex flex-col items-center text-center bg-[#E7E8D1]">
                            {/* Height */}
                            {player.roster_height && (
                              <div className="text-xs text-black mb-1">
                                <span className="font-bold">Height:</span> {player.roster_height}
                              </div>
                            )}
                            {/* Hometown */}
                            {player.hometown && (
                              <div className="text-xs text-black mb-1 truncate">
                                <span className="font-bold">From:</span> {player.hometown}
                              </div>
                            )}
                            {/* Conference */}
                            {player.conf && (
                              <div className="text-xs text-black mb-1 truncate">
                                <span className="font-bold">Conf:</span> {player.conf}
                              </div>
                            )}
                            {/* Additional teams */}
                            {getPlayerTeams(player).length > 1 && (
                              <div className="text-xs text-black truncate mt-2">
                                <span className="font-bold">Also:</span> {getPlayerTeams(player).slice(1).join(', ')}
                              </div>
                            )}
                            {/* Additional years */}
                            {getPlayerYears(player).length > 1 && (
                              <div className="text-xs text-black">
                                <span className="font-bold">Years:</span> {getPlayerYears(player).join(', ')}
                              </div>
                            )}

                            <div className="text-xs text-black mt-2 italic">
                              Click to flip back
                            </div>
                          </div>

                          {/* Card footer with team secondary color */}
                          <div
                            className="absolute bottom-0 left-0 right-0 h-2"
                            style={{
                              backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').secondary
                            }}
                          ></div>

                          {/* Step number badge */}
                          <div className="absolute -top-2 -right-2 w-7 h-7 bg-black text-white text-xs font-bold flex items-center justify-center border-2 border-white shadow-[3px_3px_0px_black]">
                            {index + 1}
                          </div>
                        </div>
                      </div>
                    </div>
                    {index < playerChain.length - 1 && <div className="text-xs font-bold text-black">→</div>}
                  </div>
                ))}
                
                {/* Target Card */}
                {!gameEnded && (
                  <>
                    <div className="text-xs font-bold text-black">→</div>
                    <div
                      className="relative w-36 h-48 border-2 border-dashed border-red-500 shadow-[3px_3px_0px_black] opacity-70 flex flex-col items-center justify-center p-2 bg-[#E7E8D1]"
                    >
                      <div className="text-xs font-bold text-red-600 mb-2 uppercase tracking-wide">TARGET</div>
                      <div className="font-bold text-xs text-black mb-1 line-clamp-2 leading-tight text-center">
                        {getPlayerName(gamePair.end_player)}
                      </div>
                      {getPlayerTeams(gamePair.end_player).length > 0 && (
                        <div className="text-xs text-black truncate text-center">
                          {getPlayerTeams(gamePair.end_player)[0]}
                        </div>
                      )}
                      {getPlayerYears(gamePair.end_player).length > 0 && (
                        <div className="text-xs text-black font-bold text-center">
                          {getPlayerYears(gamePair.end_player)[0]}
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Input */}
            {gameStarted && (
              <div ref={searchInputRef} className="relative">
                <input
                  type="text"
                  value={currentInput}
                  onChange={handleInputChange}
                  placeholder="Enter a teammate of the current player..."
                  className="w-full border-2 border-black p-3 font-mono bg-[#E7E8D1] focus:shadow-[3px_3px_0px_black]"
                  autoFocus
                />

                {showSearchResults && searchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 bg-[#E7E8D1] border-2 border-black border-t-0 max-h-60 overflow-y-auto z-10 shadow-[3px_3px_0px_black]">
                    {searchResults.map((player, index) => (
                      <div
                        key={getPlayerId(player)}
                        onClick={() => selectPlayer(player)}
                        className="p-3 hover:bg-[#B8C0A8] cursor-pointer border-b-2 border-black last:border-b-0"
                      >
                        <div className="font-bold">{getPlayerName(player)}</div>
                        {getPlayerTeams(player).length > 0 && (
                          <div className="text-xs text-black">{getPlayerTeams(player).slice(0, 3).join(', ')}{getPlayerTeams(player).length > 3 ? '...' : ''}</div>
                        )}
                        {getPlayerYears(player).length > 0 && (
                          <div className="text-xs text-black">{getPlayerYears(player).join(', ')}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className="bg-[#E7E8D1] border-2 border-black p-3 shadow-[3px_3px_0px_black]">
                {error}
              </div>
            )}

            {/* Success message */}
            {gameEnded && playerChain[playerChain.length - 1].id === gamePair.end_player.id && (
              <div className="bg-[#E7E8D1] border-2 border-black p-4 shadow-[3px_3px_0px_black]">
                <div className="font-bold text-center uppercase tracking-wide">Congratulations! You completed the path!</div>
                <div className="text-center mt-2">Time: {formatTime(timeElapsed)}</div>
                <div className="text-center">Steps: {playerChain.length - 1}</div>
              </div>
            )}

            {/* Shortest path (when gave up) */}
            {shortestPath && (
              <div className="bg-[#E7E8D1] border-2 border-black p-4 shadow-[3px_3px_0px_black]">
                <h2 className="font-bold mb-3 text-center uppercase tracking-wide">Shortest Path:</h2>
                <div className="flex flex-wrap justify-center items-center gap-4">
                  {shortestPath.map((player, index) => (
                    <div key={getPlayerId(player)} className="flex items-center gap-4">
                      {/* Collectible Card */}
                      <div
                        className={`
                          relative group cursor-pointer card-flip-container
                          transition-all duration-300
                        `}
                        style={{
                          width: '144px',
                          height: '192px'
                        }}
                        onClick={() => toggleCardFlip(`shortest-${index}`)}
                      >
                        <div className={`card-flip-inner ${flippedCards.has(`shortest-${index}`) ? 'flipped' : ''}`}>
                          {/* Front of card */}
                          <div
                            className="card-flip-front relative w-36 h-48 border-2 border-black shadow-[3px_3px_0px_black] hover:shadow-[3px_3px_0px_black] transition-all duration-300 overflow-hidden bg-[#E7E8D1]"
                          >
                            {/* Card header with team primary color */}
                            <div
                              className="text-white p-2 text-center"
                              style={{
                                backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').primary
                              }}
                            >
                              <div className="text-xs font-bold tracking-wider truncate uppercase">
                                {getPlayerTeams(player)[0] || 'Unknown'}
                              </div>
                            </div>

                            {/* Player info */}
                            <div className="p-3 flex flex-col items-center text-center bg-[#E7E8D1]">
                              {/* Player name */}
                              <div className="font-bold text-xs text-black mb-1 line-clamp-2 leading-tight">
                                {getPlayerName(player)}
                              </div>

                              {/* Position */}
                              {player.Position && (
                                <div className="text-xs text-black font-bold mb-1">
                                  {player.Position}
                                </div>
                              )}

                              {/* Team */}
                              {getPlayerTeams(player).length > 0 && (
                                <div className="text-xs text-black font-medium mb-1 truncate">
                                  {getPlayerTeams(player)[0]}
                                </div>
                              )}

                              {/* Year */}
                              {getPlayerYears(player).length > 0 && (
                                <div className="text-xs text-black font-bold">
                                  {getPlayerYears(player)[0]}
                                </div>
                              )}

                              <div className="text-xs text-black mt-2 italic">
                                Click for more info
                              </div>
                            </div>

                            {/* Card footer with team secondary color */}
                            <div
                              className="absolute bottom-0 left-0 right-0 h-2"
                              style={{
                                backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').secondary
                              }}
                            ></div>

                            {/* Step number badge */}
                            <div className="absolute -top-2 -right-2 w-7 h-7 bg-black text-white text-xs font-bold flex items-center justify-center border-2 border-white shadow-[3px_3px_0px_black]">
                              {index + 1}
                            </div>
                          </div>

                          {/* Back of card */}
                          <div
                            className="card-flip-back relative w-36 h-48 border-2 border-black shadow-[3px_3px_0px_black] overflow-hidden bg-[#E7E8D1]"
                          >
                            {/* Card header with team primary color */}
                            <div
                              className="text-white p-2 text-center"
                              style={{
                                backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').primary
                              }}
                            >
                              <div className="text-xs font-bold tracking-wider truncate uppercase">
                                {getPlayerName(player)}
                              </div>
                            </div>

                            {/* Player details */}
                            <div className="p-3 flex flex-col items-center text-center bg-[#E7E8D1]">
                              {/* Height */}
                              {player.roster_height && (
                                <div className="text-xs text-black mb-1">
                                  <span className="font-bold">Height:</span> {player.roster_height}
                                </div>
                              )}
                              {/* Hometown */}
                              {player.hometown && (
                                <div className="text-xs text-black mb-1 truncate">
                                  <span className="font-bold">From:</span> {player.hometown}
                                </div>
                              )}
                              {/* Conference */}
                              {player.conf && (
                                <div className="text-xs text-black mb-1 truncate">
                                  <span className="font-bold">Conf:</span> {player.conf}
                                </div>
                              )}
                              {/* Additional teams */}
                              {getPlayerTeams(player).length > 1 && (
                                <div className="text-xs text-black truncate mt-2">
                                  <span className="font-bold">Also:</span> {getPlayerTeams(player).slice(1).join(', ')}
                                </div>
                              )}
                              {/* Additional years */}
                              {getPlayerYears(player).length > 1 && (
                                <div className="text-xs text-black">
                                  <span className="font-bold">Years:</span> {getPlayerYears(player).join(', ')}
                                </div>
                              )}

                              <div className="text-xs text-black mt-2 italic">
                                Click to flip back
                              </div>
                            </div>

                            {/* Card footer with team secondary color */}
                            <div
                              className="absolute bottom-0 left-0 right-0 h-2"
                              style={{
                                backgroundColor: getTeamColor(getPlayerTeams(player)[0] || '').secondary
                              }}
                            ></div>

                            {/* Step number badge */}
                            <div className="absolute -top-2 -right-2 w-7 h-7 bg-black text-white text-xs font-bold flex items-center justify-center border-2 border-white shadow-[3px_3px_0px_black]">
                              {index + 1}
                            </div>
                          </div>
                        </div>
                      </div>
                      {index < shortestPath.length - 1 && <div className="text-xs font-bold text-black">→</div>}
                    </div>
                  ))}
                </div>
                <div className="mt-3 font-bold text-center uppercase tracking-wide">
                  Optimal steps: {shortestPath.length - 1}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      
      <style jsx global>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        @keyframes pop {
          0% { transform: scale(0.8); opacity: 0; }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); opacity: 1; }
        }
        
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
        
        .animate-pop {
          animation: pop 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
