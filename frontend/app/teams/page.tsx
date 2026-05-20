"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAllTeams } from "@/lib/api";

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

  useEffect(() => {
    fetchAllTeams()
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
        console.error("Error fetching teams:", err);
        setError("Failed to load teams");
        setLoading(false);
      });
  }, []);

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
        <h1 className="text-3xl font-bold mb-2">Teams</h1>
        <p className="text-sm text-gray-600">{teams.length} teams across {Object.keys(teamsByConference).length} conferences</p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search teams by name, mascot, or abbreviation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-black rounded-lg bg-white text-black focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>

      {/* Expand/Collapse All Buttons */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={expandAll}
          className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          Expand All
        </button>
        <button
          onClick={collapseAll}
          className="px-4 py-2 bg-white text-black border border-black rounded-lg hover:bg-gray-100 transition-colors"
        >
          Collapse All
        </button>
      </div>

      {sortedConferences.map(([conference, conferenceTeams]) => {
        const isExpanded = expandedConferences[conference] !== false;
        
        return (
          <div key={conference} className="border border-black rounded-lg p-4">
            <div 
              className="flex items-center justify-between cursor-pointer mb-4"
              onClick={() => toggleConference(conference)}
            >
              <h2 className="text-xl font-bold">{conference}</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">{conferenceTeams.length} teams</span>
                <span className="text-xl">{isExpanded ? "−" : "+"}</span>
              </div>
            </div>
            
            {isExpanded && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {conferenceTeams
                  .sort((a, b) => (a.school || "").localeCompare(b.school || ""))
                  .map((team) => (
                    <Link
                      key={team.id}
                      href={`/team/${team.id}`}
                      className="bg-[#E7E8D1] hover:bg-[#dfe2c6] border border-black p-3 rounded transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-bold text-sm">{team.display_name || team.school}</div>
                          {team.abbreviation && (
                            <div className="text-xs text-gray-600">{team.abbreviation}</div>
                          )}
                        </div>
                        {team.mini_stats && (
                          <div className="text-xs font-mono">
                            {team.mini_stats.wins !== null && team.mini_stats.losses !== null ? (
                              <span>{team.mini_stats.wins}-{team.mini_stats.losses}</span>
                            ) : (
                              <span className="text-gray-400">N/A</span>
                            )}
                          </div>
                        )}
                      </div>
                      {team.mini_stats && (
                        <div className="grid grid-cols-3 gap-2 text-xs mt-2 pt-2 border-t border-black/20">
                          <div className="text-center">
                            <div className="text-gray-500">Net</div>
                            <div className="font-mono">
                              {team.mini_stats.adj_net !== null ? team.mini_stats.adj_net.toFixed(1) : 'N/A'}
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-gray-500">Off</div>
                            <div className="font-mono">
                              {team.mini_stats.off_adj_ppp !== null ? team.mini_stats.off_adj_ppp.toFixed(1) : 'N/A'}
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-gray-500">Def</div>
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
  );
}
