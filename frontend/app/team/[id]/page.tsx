"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchTeam } from "@/lib/api";
import { useYear } from "@/app/context/YearContext";

import TeamHeader from "@/components/team/TeamHeader";
import TeamResumePanel from "@/components/team/TeamResumePanel";
import TeamAnalyticsPanel from "@/components/team/TeamAnalyticsPanel";
import TeamRosterPanel from "@/components/team/TeamRosterPanel";
import TeamLocationPanel from "@/components/team/TeamLocationPanel";
import TeamStylePanel from "@/components/team/TeamStylePanel";
import TeamNilPanel from "@/components/team/TeamNilPanel";

export default function TeamPage() {
  const { id } = useParams();
  const { year, setYear } = useYear();

  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  useEffect(() => {
    if (!id) return;

    fetchTeam(id as string, year)
      .then((data: any) => {
        setTeam(data.team);
        setAvailableYears(data.available_years || []);
        setLoading(false);
      })
      .catch((err: any) => {
        setError("Failed to load team data");
        setLoading(false);
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
    <div className="p-2 sm:p-3 space-y-6">
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
            className="bg-white border-2 border-black px-2 py-1 font-mono text-black transition-all duration-200 text-xs"
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
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

        {/* NIL VALUATIONS - Full width at bottom */}
        <div className="md:col-span-2">
          <TeamNilPanel teamId={id as string} year={year} />
        </div>
      </div>
    </div>
  );
}
