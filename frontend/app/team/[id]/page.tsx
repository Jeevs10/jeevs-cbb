"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchTeam, fetchAllTeams } from "@/lib/api";
import { useYear } from "@/app/context/YearContext";

import TeamHeader from "@/components/team/TeamHeader";
import TeamResumePanel from "@/components/team/TeamResumePanel";
import TeamAnalyticsPanel from "@/components/team/TeamAnalyticsPanel";
import TeamRosterPanel from "@/components/team/TeamRosterPanel";
import TeamLocationPanel from "@/components/team/TeamLocationPanel";
import TeamStylePanel from "@/components/team/TeamStylePanel";
import TeamMatchupsPanel from "@/components/team/TeamMatchupsPanel";
import TeamSimilarPanel from "@/components/team/TeamSimilarPanel";
import TeamNilPanel from "@/components/team/TeamNilPanel";

export default function TeamPage() {
  const { id } = useParams();
  const { year, setYear } = useYear();

  const [team, setTeam] = useState<any>(null);
  const [allTeams, setAllTeams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [styleWeight, setStyleWeight] = useState<number>(0.5);

  useEffect(() => {
    if (!id) return;

    // Fetch all teams for matchups
    fetchTeam(id as string, year)
      .then((data: any) => {
        console.log("Team data received:", data);
        setTeam(data.team);
        setAvailableYears(data.available_years || []);
        setLoading(false);
      })
      .catch((err: any) => {
        console.error("Error fetching team:", err);
        setError("Failed to load team data");
        setLoading(false);
      });

    // Fetch all teams for matchups
    fetchAllTeams(year)
      .then((data: any) => {
        console.log("All teams data:", data);
        if (data.results) {
          setAllTeams(data.results);
        }
      })
      .catch(err => {
        console.error("Error fetching all teams:", err);
      });
  }, [id, year]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING TEAM DATA...
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        {error}
      </div>
    );
  }

  if (!team) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        TEAM NOT FOUND
      </div>
    );
  }

  return (
    <div className="p-3 space-y-6">
      <TeamHeader team={team} />

      {/* YEAR SELECTOR */}
      {availableYears.length > 0 && (
        <div className="flex items-center gap-2 text-xs font-bold">
          <span>Season:</span>
          <select
            value={year ?? ""}
            onChange={(e) => {
              const value = e.target.value;
              setYear(value === "" ? null : Number(value));
            }}
            className="bg-white border-2 border-black px-2 py-1 font-mono text-black"
          >
            <option value="">Latest</option>
            {availableYears.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="text-xs font-bold">
        Viewing: {year ?? "Latest Season"}
      </div>

      <div className="text-xs font-bold">
        {team.analytics_available ? "Analytics Available" : "Basic Team Info Only"}
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* RESUME */}
        <TeamResumePanel analytics={team.analytics} />

        {/* ANALYTICS */}
        <TeamAnalyticsPanel analytics={team.analytics} />

        {/* ROSTER */}
        <TeamRosterPanel roster={team.roster} year={year} />

        {/* LOCATION - Where style was */}
        {team.current_city && team.current_state && (
          <TeamLocationPanel
            city={team.current_city}
            state={team.current_state}
            primaryColor={team.primary_color}
          />
        )}

        {/* STYLE - Full width, scrollable */}
        {team.analytics && (
          <div className="md:col-span-2 max-h-[400px] overflow-y-auto">
            <TeamStylePanel analytics={team.analytics} />
          </div>
        )}

        {/* MATCHUPS - Full width, scrollable */}
        {team.analytics && allTeams.length > 0 && (
          <div className="md:col-span-2 max-h-[400px] overflow-y-auto">
            <TeamMatchupsPanel currentTeam={team} allTeams={allTeams} />
          </div>
        )}

        {/* SIMILAR TEAMS */}
        {team.analytics && (
          <div className="md:col-span-2">
            <TeamSimilarPanel currentTeam={team} styleWeight={styleWeight} setStyleWeight={setStyleWeight} />
          </div>
        )}

        {/* NIL VALUATIONS - Full width at bottom */}
        <div className="md:col-span-2">
          <TeamNilPanel teamId={id as string} year={year} />
        </div>
      </div>
    </div>
  );
}
