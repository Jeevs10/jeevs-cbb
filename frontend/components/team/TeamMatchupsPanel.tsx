"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Panel, { PanelHeader } from "@/components/ui/Panel";

interface Matchup {
  team: string;
  team_id: string;
  overall_score: number;
  offensive_score: number;
  defensive_score: number;
  offensive_reasons: string[];
  defensive_reasons: string[];
}

function getMatchupGrade(score: number): { grade: string; color: string; bgColor: string } {
  // Scale from -1 to 1
  // Positive = favorable matchup, Negative = unfavorable matchup
  
  if (score >= 0.35) return { grade: "Elite", color: "text-green-900", bgColor: "bg-green-100" };
  if (score >= 0.25) return { grade: "Strong", color: "text-green-700", bgColor: "bg-green-50" };
  if (score >= 0.15) return { grade: "Plus", color: "text-green-600", bgColor: "bg-green-50" };
  if (score >= 0.05) return { grade: "Edge", color: "text-lime-600", bgColor: "bg-lime-50" };
  if (score >= -0.05) return { grade: "Even", color: "text-gray-600", bgColor: "bg-gray-50" };
  if (score >= -0.15) return { grade: "Minus", color: "text-orange-600", bgColor: "bg-orange-50" };
  if (score >= -0.25) return { grade: "Weak", color: "text-orange-700", bgColor: "bg-orange-100" };
  if (score >= -0.35) return { grade: "Liability", color: "text-red-700", bgColor: "bg-red-100" };
  return { grade: "Fatal", color: "text-red-900", bgColor: "bg-red-200" };
}

type FilterType = "all" | "conference" | "quartile";
type TabType = "overview" | "opponent";

export default function TeamMatchupsPanel({ currentTeam, allTeams }: { currentTeam: any; allTeams?: any[] }) {
  const [mostEffective, setMostEffective] = useState<Matchup[]>([]);
  const [leastEffective, setLeastEffective] = useState<Matchup[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<FilterType>("all");
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [selectedOpponentId, setSelectedOpponentId] = useState<string>("");
  const [singleMatchup, setSingleMatchup] = useState<Matchup | null>(null);

  useEffect(() => {
    if (!currentTeam?.id) {
      setLoading(false);
      return;
    }

    const fetchMatchups = async () => {
      try {
        setLoading(true);
        
        const response = await fetch(`http://localhost:8000/api/v1/teams/${currentTeam.id}/matchups?filter_type=${filterType}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch matchups: ${response.status}`);
        }
        
        const data = await response.json();
        
        setMostEffective(data.matchups?.most_effective_against || []);
        setLeastEffective(data.matchups?.least_effective_against || []);
      } catch (err) {
        // Handle error silently
      } finally {
        setLoading(false);
      }
    };

    fetchMatchups();
  }, [currentTeam?.id, filterType]);

  // Fetch specific opponent matchup
  useEffect(() => {
    if (!selectedOpponentId || !currentTeam?.id) {
      setSingleMatchup(null);
      return;
    }

    const fetchSingleMatchup = async () => {
      try {
        setLoading(true);

        const response = await fetch(`http://localhost:8000/api/v1/teams/${currentTeam.id}/matchup/${selectedOpponentId}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch matchup: ${response.status}`);
        }

        const data = await response.json();
        setSingleMatchup(data.matchup || null);
      } catch (err) {
        setSingleMatchup(null);
      } finally {
        setLoading(false);
      }
    };

    fetchSingleMatchup();
  }, [selectedOpponentId, currentTeam?.id]);

  if (loading) {
    return (
      <Panel className="mt-6">
        <PanelHeader>STYLE MATCHUP</PanelHeader>
        <div className="p-3 text-xs text-center opacity-60">
          Loading matchups...
        </div>
      </Panel>
    );
  }

  if (mostEffective.length === 0 && leastEffective.length === 0) {
    return (
      <Panel className="mt-6">
        <PanelHeader>STYLE MATCHUP</PanelHeader>
        <div className="p-3 text-xs text-center opacity-60">
          No matchup data available
        </div>
      </Panel>
    );
  }

  return (
    <Panel className="mt-6">
      <PanelHeader>STYLE MATCHUP</PanelHeader>
      
      <div className="p-3">
        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-3 py-1 text-xs rounded ${
              activeTab === "overview"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("opponent")}
            className={`px-3 py-1 text-xs rounded ${
              activeTab === "opponent"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            vs Opponent
          </button>
        </div>

        {/* Opponent Selector Tab */}
        {activeTab === "opponent" && allTeams && allTeams.length > 0 && (
          <div className="mb-4">
            <label className="text-xs font-bold mb-1 block">Select Opponent:</label>
            <select
              value={selectedOpponentId}
              onChange={(e) => setSelectedOpponentId(e.target.value)}
              className="w-full bg-white border-2 border-black px-2 py-1 text-xs font-mono"
            >
              <option value="">-- Select Opponent --</option>
              {allTeams
                .filter((team) => team.id !== currentTeam?.id)
                .sort((a, b) => a.school.localeCompare(b.school))
                .map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.school}
                  </option>
                ))}
            </select>
          </div>
        )}

        {/* Filter Buttons (Overview Tab Only) */}
        {activeTab === "overview" && (
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setFilterType("all")}
              className={`px-3 py-1 text-xs rounded ${
                filterType === "all"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              All Teams
            </button>
            <button
              onClick={() => setFilterType("conference")}
              className={`px-3 py-1 text-xs rounded ${
                filterType === "conference"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Same Conference
            </button>
            <button
              onClick={() => setFilterType("quartile")}
              className={`px-3 py-1 text-xs rounded ${
                filterType === "quartile"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Same Quartile
            </button>
          </div>
        )}
      </div>

      {/* Overview Tab Content */}
      {activeTab === "overview" && (
        <div className="px-3 pb-3 space-y-4">
          {mostEffective.length > 0 && (
            <div>
              <div className="text-xs font-bold text-green-700 mb-2 flex items-center gap-2">
                <span className="text-lg">⚔️</span>
                MOST EFFECTIVE AGAINST
              </div>
              <div className="text-[10px] text-gray-600 mb-2">
                Teams that match up poorly with our strengths on both offense and defense
              </div>
              <div className="space-y-3">
                {mostEffective.map((matchup, idx) => {
                  const { grade, color, bgColor } = getMatchupGrade(matchup.overall_score);
                  return (
                    <Link
                      key={idx}
                      href={`/player/${matchup.team_id}`}
                      className="block"
                    >
                      <div className={`border border-black p-2 rounded ${bgColor} hover:opacity-80 transition`}>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-bold">
                            {matchup.team}
                          </span>
                          <span className={`text-lg font-bold ${color}`}>
                            {grade}
                          </span>
                        </div>
                      <div className="space-y-1">
                        {matchup.offensive_reasons.length > 0 && (
                          <div className="text-[10px] text-gray-700">
                            <span className="font-semibold">Offense:</span> {matchup.offensive_reasons.join("; ")}
                          </div>
                        )}
                        {matchup.defensive_reasons.length > 0 && (
                          <div className="text-[10px] text-gray-700">
                            <span className="font-semibold">Defense:</span> {matchup.defensive_reasons.join("; ")}
                          </div>
                        )}
                      </div>
                    </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}

          {leastEffective.length > 0 && (
            <div>
              <div className="text-xs font-bold text-red-700 mb-2 flex items-center gap-2">
                <span className="text-lg">🛡️</span>
                LEAST EFFECTIVE AGAINST
              </div>
              <div className="text-[10px] text-gray-600 mb-2">
                Teams that exploit our weaknesses on both offense and defense
              </div>
              <div className="space-y-3">
                {leastEffective.map((matchup, idx) => {
                  const { grade, color, bgColor } = getMatchupGrade(matchup.overall_score);
                  return (
                    <Link
                      key={idx}
                      href={`/player/${matchup.team_id}`}
                      className="block"
                    >
                      <div className={`border border-black p-2 rounded ${bgColor} hover:opacity-80 transition`}>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-bold">
                            {matchup.team}
                          </span>
                          <span className={`text-lg font-bold ${color}`}>
                            {grade}
                          </span>
                        </div>
                      <div className="space-y-1">
                        {matchup.offensive_reasons.length > 0 && (
                          <div className="text-[10px] text-gray-700">
                            <span className="font-semibold">Offense:</span> {matchup.offensive_reasons.join("; ")}
                          </div>
                        )}
                        {matchup.defensive_reasons.length > 0 && (
                          <div className="text-[10px] text-gray-700">
                            <span className="font-semibold">Defense:</span> {matchup.defensive_reasons.join("; ")}
                          </div>
                        )}
                      </div>
                    </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Opponent Tab Content */}
      {activeTab === "opponent" && singleMatchup && (
        <div className="px-3 pb-3">
          <Link
            href={`/player/${singleMatchup.team_id}`}
            className="block"
          >
            <div className={`border border-black p-4 rounded ${getMatchupGrade(singleMatchup.overall_score).bgColor} hover:opacity-80 transition`}>
              <div className="flex justify-between items-center mb-4">
                <div>
                  <span className="text-sm font-bold">
                    {singleMatchup.team}
                  </span>
                <div className="text-xs text-gray-600">
                  {currentTeam?.school} vs {singleMatchup.team}
                </div>
              </div>
              <span className={`text-2xl font-bold ${getMatchupGrade(singleMatchup.overall_score).color}`}>
                {getMatchupGrade(singleMatchup.overall_score).grade}
              </span>
            </div>
            <div className="space-y-2">
              {singleMatchup.offensive_reasons.length > 0 && (
                <div className="text-xs text-gray-700">
                  <span className="font-semibold">Offense:</span> {singleMatchup.offensive_reasons.join("; ")}
                </div>
              )}
              {singleMatchup.defensive_reasons.length > 0 && (
                <div className="text-xs text-gray-700">
                  <span className="font-semibold">Defense:</span> {singleMatchup.defensive_reasons.join("; ")}
                </div>
              )}
            </div>
          </div>
          </Link>
        </div>
      )}

      {activeTab === "opponent" && !singleMatchup && selectedOpponentId && (
        <div className="px-3 pb-3 text-xs text-center opacity-60">
          No matchup data available for this opponent
        </div>
      )}
    </Panel>
  );
}

