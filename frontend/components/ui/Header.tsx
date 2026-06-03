"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef } from "react";

export function Header() {
  const pathname = usePathname();
  const [playerDropdownOpen, setPlayerDropdownOpen] = useState(false);
  const [teamDropdownOpen, setTeamDropdownOpen] = useState(false);
  const [projectionsDropdownOpen, setProjectionsDropdownOpen] = useState(false);
  const playerTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const teamTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const projectionsTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handlePlayerMouseEnter = () => {
    if (playerTimeoutRef.current) {
      clearTimeout(playerTimeoutRef.current);
      playerTimeoutRef.current = null;
    }
    setPlayerDropdownOpen(true);
  };

  const handlePlayerMouseLeave = () => {
    playerTimeoutRef.current = setTimeout(() => {
      setPlayerDropdownOpen(false);
    }, 200);
  };

  const handleTeamMouseEnter = () => {
    if (teamTimeoutRef.current) {
      clearTimeout(teamTimeoutRef.current);
      teamTimeoutRef.current = null;
    }
    setTeamDropdownOpen(true);
  };

  const handleTeamMouseLeave = () => {
    teamTimeoutRef.current = setTimeout(() => {
      setTeamDropdownOpen(false);
    }, 200);
  };

  const handleProjectionsMouseEnter = () => {
    if (projectionsTimeoutRef.current) {
      clearTimeout(projectionsTimeoutRef.current);
      projectionsTimeoutRef.current = null;
    }
    setProjectionsDropdownOpen(true);
  };

  const handleProjectionsMouseLeave = () => {
    projectionsTimeoutRef.current = setTimeout(() => {
      setProjectionsDropdownOpen(false);
    }, 200);
  };

  return (
    <header className="border-b-2 border-black bg-[#C7D0B8]">
      <div className="px-4">
        <div className="flex justify-between items-center h-12">
          {/* Logo/Title */}
          <Link href="/" className="text-xs font-bold text-black hover:underline uppercase tracking-wide">
            CBB Stats
          </Link>

          {/* Navigation */}
          <nav className="flex space-x-6">
            <Link
              href="/"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/" ? "text-black" : "text-black"
              }`}
            >
              Home
            </Link>

            {/* Player Dropdown */}
            <div
              className="relative"
              onMouseEnter={handlePlayerMouseEnter}
              onMouseLeave={handlePlayerMouseLeave}
            >
              <button className="text-xs font-medium transition-colors hover:underline text-black">
                Player
              </button>
              {playerDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-[#E7E8D1] border-2 border-black shadow-[3px_3px_0px_black] z-10">
                  <Link
                    href="/leaderboard/basic"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Basic Leaderboard
                  </Link>
                  <Link
                    href="/leaderboard/advanced"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Advanced Leaderboard
                  </Link>
                  <Link
                    href="/moves"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Moves Rankings
                  </Link>
                  <Link
                    href="/similarity"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Similarity Map
                  </Link>
                </div>
              )}
            </div>

            {/* Team Dropdown */}
            <div
              className="relative"
              onMouseEnter={handleTeamMouseEnter}
              onMouseLeave={handleTeamMouseLeave}
            >
              <button className="text-xs font-medium transition-colors hover:underline text-black">
                Team
              </button>
              {teamDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-[#E7E8D1] border-2 border-black shadow-[3px_3px_0px_black] z-10">
                  <Link
                    href="/team-rankings"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Team Rankings
                  </Link>
                  <Link
                    href="/teams"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Team Catalog
                  </Link>
                </div>
              )}
            </div>

            <Link
              href="/game"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/game" ? "text-black" : "text-black"
              }`}
            >
              Game
            </Link>

            {/* Projections Dropdown */}
            <div
              className="relative"
              onMouseEnter={handleProjectionsMouseEnter}
              onMouseLeave={handleProjectionsMouseLeave}
            >
              <button className="text-xs font-medium transition-colors hover:underline text-black">
                Projections
              </button>
              {projectionsDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-[#E7E8D1] border-2 border-black shadow-[3px_3px_0px_black] z-10">
                  <Link
                    href="/projections/2027"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    2027 Projections
                  </Link>
                  <Link
                    href="/projections/leaderboard"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Projection Leaderboard
                  </Link>
                </div>
              )}
            </div>

            <Link
              href="/clusters"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/clusters" ? "text-black" : "text-black"
              }`}
            >
              Cluster Analysis
            </Link>

            <Link
              href="/clusters/leaderboard"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/clusters/leaderboard" ? "text-black" : "text-black"
              }`}
            >
              Cluster Leaderboard
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
