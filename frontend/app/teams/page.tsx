"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAllTeams } from "@/lib/api";
import { useYear } from "@/app/context/YearContext";

interface MiniStats {
  wins: number | null;
  losses: number | null;
  adj_net: number | null;
  off_adj_ppp: number | null;
  def_adj_ppp: number | null;
}

interface Team {
  id: string;
  school: string;
  mascot: string | null;
  abbreviation: string | null;
  display_name: string | null;
  conference: string | null;
  mini_stats: MiniStats | null;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedConferences, setExpandedConferences] = useState<Record<string, boolean>>({});
  const { year, setYear } = useYear();

  useEffect(() => {
    setLoading(true);
    fetchAllTeams(year)
      .then((data: any) => {
        setTeams(data.results || []);
        // Initialize all conferences as expanded by default
        const teamsByConference = (data.results || []).reduce((acc: Record<string, any[]>, team: any) => {
          const conference = team.conference || "Other";
          if (!acc[conference]) {
            acc[conference] = [];
          }
          acc[conference].push(team);
          return acc;
        }, {});

        setExpandedConferences(
          Object.keys(teamsByConference).reduce((acc: Record<string, boolean>, conf: string) => {
            acc[conf] = true;
            return acc;
          }, {})
        );
        setLoading(false);
      })
      .catch((err: any) => {
        setError("Failed to load teams");
        setLoading(false);
      });
  }, [year]);

  // Toggle conference expansion
  const toggleConference = (conference: string) => {
    setExpandedConferences(prev => ({
      ...prev,
      [conference]: !prev[conference]
    }));
  };

  // Expand all conferences
  const expandAll = () => {
    const teamsByConference = teams.reduce((acc, team) => {
      const conference = team.conference || "Other";
      if (!acc[conference]) {
        acc[conference] = [];
      }
      acc[conference].push(team);
      return acc;
    }, {} as Record<string, Team[]>);
    
    setExpandedConferences(
      Object.keys(teamsByConference).reduce((acc, conf) => {
        acc[conf] = true;
        return acc;
      }, {} as Record<string, boolean>)
    );
  };

  // Collapse all conferences
  const collapseAll = () => {
    const teamsByConference = teams.reduce((acc, team) => {
      const conference = team.conference || "Other";
      if (!acc[conference]) {
        acc[conference] = [];
      }
      acc[conference].push(team);
      return acc;
    }, {} as Record<string, Team[]>);
    
    setExpandedConferences(
      Object.keys(teamsByConference).reduce((acc, conf) => {
        acc[conf] = false;
        return acc;
      }, {} as Record<string, boolean>)
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING TEAMS...
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

  // Filter teams by search query
  const filteredTeams = teams.filter(team => {
    const query = searchQuery.toLowerCase();
    return (
      (team.school?.toLowerCase() || "").includes(query) ||
      (team.display_name?.toLowerCase() || "").includes(query) ||
      (team.mascot?.toLowerCase() || "").includes(query) ||
      (team.abbreviation?.toLowerCase() || "").includes(query)
    );
  });

  // Group teams by conference
  const teamsByConference = filteredTeams.reduce((acc, team) => {
    const conference = team.conference || "Other";
    if (!acc[conference]) {
      acc[conference] = [];
    }
    acc[conference].push(team);
    return acc;
  }, {} as Record<string, Team[]>);

  const sortedConferences = Object.entries(teamsByConference)
    .sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className="p-3 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-xs font-bold mb-2 uppercase tracking-wide">Teams</h1>
        <p className="text-xs text-black">{teams.length} teams across {Object.keys(teamsByConference).length} conferences</p>
      </div>

      {/* Year Selector */}
      <div className="flex items-center gap-2 text-xs font-bold">
        <span>Season:</span>
        <select
          value={year ?? ""}
          onChange={(e) => {
            const value = e.target.value;
            setYear(value === "" ? null : Number(value));
          }}
          className="bg-white border-2 border-black px-2 py-1 font-mono text-black transition-all duration-200"
        >
          <option value="">Latest</option>
          <option value="2019">2019</option>
          <option value="2020">2020</option>
          <option value="2021">2021</option>
          <option value="2022">2022</option>
          <option value="2023">2023</option>
          <option value="2024">2024</option>
          <option value="2025">2025</option>
          <option value="2026">2026</option>
        </select>
      </div>

      <div className="text-xs font-bold">
        Viewing: {year ?? "Latest Season"}
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search teams by name, mascot, or abbreviation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border-2 border-black bg-[#E7E8D1] text-black focus:outline-none focus:shadow-[3px_3px_0px_black] transition-all duration-200"
        />
      </div>

      {/* Expand/Collapse All Buttons */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={expandAll}
          className="px-4 py-2 border-2 border-black bg-black text-white font-bold hover:bg-black/80 transition-all duration-200 shadow-[3px_3px_0px_black]"
        >
          Expand All
        </button>
        <button
          onClick={collapseAll}
          className="px-4 py-2 border-2 border-black bg-[#E7E8D1] text-black font-bold hover:bg-[#B8C0A8] transition-all duration-200 shadow-[3px_3px_0px_black]"
        >
          Collapse All
        </button>
      </div>

      <div>
      {sortedConferences.map(([conference, conferenceTeams]) => {
        const isExpanded = expandedConferences[conference] !== false;

        return (
          <div key={conference} className="border-2 border-black p-4">
            <div
              className="flex items-center justify-between cursor-pointer mb-4"
              onClick={() => toggleConference(conference)}
            >
              <h2 className="text-xs font-bold uppercase tracking-wide">{conference}</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-black">{conferenceTeams.length} teams</span>
                <span className="text-xs">{isExpanded ? "−" : "+"}</span>
              </div>
            </div>

            {isExpanded && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {conferenceTeams
                  .sort((a, b) => (a.school || "").localeCompare(b.school || ""))
                  .map((team, index) => (
                    <Link
                      key={team.id}
                      href={`/team/${team.id}`}
                      className="bg-[#E7E8D1] hover:bg-[#B8C0A8] border-2 border-black p-3 transition-all duration-200 hover:shadow-[2px_2px_0px_black]"
                      style={{
                        animation: `fadeIn 0.3s ease-out ${index * 0.03}s both`
                      }}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-bold text-xs">{team.display_name || team.school}</div>
                          {team.abbreviation && (
                            <div className="text-xs text-black">{team.abbreviation}</div>
                          )}
                        </div>
                        {team.mini_stats && (
                          <div className="text-xs font-mono">
                            {team.mini_stats.wins !== null && team.mini_stats.losses !== null ? (
                              <span>{team.mini_stats.wins}-{team.mini_stats.losses}</span>
                            ) : (
                              <span className="text-black">N/A</span>
                            )}
                          </div>
                        )}
                      </div>
                      {team.mini_stats && (
                        <div className="grid grid-cols-3 gap-2 text-xs mt-2 pt-2 border-t-2 border-black">
                          <div className="text-center">
                            <div className="text-black">Net</div>
                            <div className="font-mono">
                              {team.mini_stats.adj_net !== null ? team.mini_stats.adj_net.toFixed(1) : 'N/A'}
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-black">Off</div>
                            <div className="font-mono">
                              {team.mini_stats.off_adj_ppp !== null ? team.mini_stats.off_adj_ppp.toFixed(1) : 'N/A'}
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-black">Def</div>
                            <div className="font-mono">
                              {team.mini_stats.def_adj_ppp !== null ? team.mini_stats.def_adj_ppp.toFixed(1) : 'N/A'}
                            </div>
                          </div>
                        </div>
                      )}
                    </Link>
                  ))}
              </div>
            )}
          </div>
        );
      })}
      </div>
    </div>
  );
}
