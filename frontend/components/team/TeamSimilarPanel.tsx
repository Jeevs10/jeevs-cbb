"use client";

import Link from "next/link";
import { useState, useEffect } from 'react';
import Panel, { PanelHeader } from "@/components/ui/Panel";

interface SimilarTeam {
  team: string;
  team_id: string;
  similarity: number;
  impact_similarity: number;
  style_similarity: number;
  impact_reasons: Array<{
    feature: string;
    delta: number;
  }>;
  impact_differences?: Array<{
    feature: string;
    delta: number;
  }>;
  style_reasons: Array<{
    feature: string;
    delta: number;
  }>;
  style_differences?: Array<{
    feature: string;
    delta: number;
  }>;
}

interface TeamSimilarPanelProps {
  currentTeam: any;
  styleWeight: number;
  setStyleWeight: (value: number) => void;
}

export default function TeamSimilarPanel({
  currentTeam,
  styleWeight,
  setStyleWeight,
}: TeamSimilarPanelProps) {
  const [similarTeams, setSimilarTeams] = useState<SimilarTeam[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch similar teams when style weight changes
  useEffect(() => {
    const fetchSimilarTeams = async () => {
      if (!currentTeam?.id) return;

      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/api/v1/teams/${currentTeam.id}/similar?style_weight=${styleWeight}&limit=10`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch similar teams: ${response.status}`);
        }

        const data = await response.json();
        setSimilarTeams(data.similar_teams || []);
      } catch (err) {
        console.error("Error fetching similar teams:", err);
        setSimilarTeams([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSimilarTeams();
  }, [currentTeam?.id, styleWeight]);

  // Helper to get appropriate reasons based on style weight
  const getReasons = (team: SimilarTeam) => {
    // If style weight > 0.5, show style reasons, otherwise show impact reasons
    if (styleWeight > 0.5) {
      return team.style_reasons || [];
    } else {
      return team.impact_reasons || [];
    }
  };

  // Helper to get appropriate differences based on style weight
  const getDifferences = (team: SimilarTeam) => {
    // If style weight > 0.5, show style differences, otherwise show impact differences
    if (styleWeight > 0.5) {
      return team.style_differences || [];
    } else {
      return team.impact_differences || [];
    }
  };

  return (
    <Panel className="mt-6">
      <PanelHeader>SIMILAR TEAMS</PanelHeader>
      
      <div className="p-3 space-y-2">
        {/* SLIDER */}
        <div className="text-[10px] mb-2">
          <div className="font-bold mb-1">Impact ↔ Style Balance</div>

          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={styleWeight}
            onChange={(e) => setStyleWeight(Number(e.target.value))}
            className="w-full"
          />

          <div className="flex justify-between text-[9px] opacity-70">
            <span>Impact</span>
            <span>Style</span>
          </div>
        </div>

        {/* SCROLL AREA */}
        <div className="max-h-[320px] overflow-y-auto pr-1 space-y-2">
          {loading ? (
            <div className="text-xs opacity-70">
              Loading similar teams...
            </div>
          ) : similarTeams.length === 0 ? (
            <div className="text-xs opacity-70">
              No similar teams found.
            </div>
          ) : (
            similarTeams.map((team) => (
              <Link
                key={team.team_id}
                href={`/team/${team.team_id}`}
                className="block"
              >
                <div className="flex justify-between items-start text-xs border border-black p-2 bg-[#E7E8D1] hover:bg-[#dfe3cd] transition">

                  {/* LEFT */}
                  <div className="flex-1 pr-2">
                    <div className="font-bold">
                      {team.team}
                    </div>

                    <div className="mt-2 grid grid-cols-2 gap-3 text-[9px]">
                      {/* WHY SIMILAR */}
                      <div>
                        <div className="font-bold mb-1">Why similar</div>

                        {getReasons(team).length > 0 ? (
                          getReasons(team).slice(0, 3).map((r: any, i: number) => (
                            <div key={i}>• {r.feature}</div>
                          ))
                        ) : (
                          <div>• {styleWeight > 0.5 ? 'style similarity' : 'impact similarity'}</div>
                        )}
                      </div>

                      {/* DIFFERENCES */}
                      <div>
                        <div className="font-bold mb-1">Key differences</div>

                        {getDifferences(team).length > 0 ? (
                          getDifferences(team).slice(0, 3).map((d: any, i: number) => (
                            <div key={i}>• {d.feature}</div>
                          ))
                        ) : (
                          <div>• minimal differences</div>
                        )}
                      </div>

                    </div>
                  </div>

                  {/* RIGHT */}
                  <div className="text-right font-bold w-16">
                    {((team.similarity ?? 0) * 100).toFixed(1)}%
                  </div>

                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </Panel>
  );
}
