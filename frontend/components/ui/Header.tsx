"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef } from "react";

export function Header() {
  const pathname = usePathname();
  const [playerDropdownOpen, setPlayerDropdownOpen] = useState(false);
  const [teamDropdownOpen, setTeamDropdownOpen] = useState(false);
  const playerTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const teamTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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

  return (
    <header className="border-b border-black bg-[#C7D0B8]">
      <div className="px-4">
        <div className="flex justify-between items-center h-12">
          {/* Logo/Title */}
          <Link href="/" className="text-lg font-bold text-black hover:underline">
            CBB Stats
          </Link>

          {/* Navigation */}
          <nav className="flex space-x-6">
            <Link
              href="/"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/" ? "text-black" : "text-gray-600"
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
              <button className="text-xs font-medium transition-colors hover:underline text-gray-600">
                Player
              </button>
              {playerDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-white border-2 border-black shadow-lg z-10">
                  <Link
                    href="/leaderboard/basic"
                    className="block px-4 py-2 text-xs hover:bg-[#E7E8D1]"
                  >
                    Basic Leaderboard
                  </Link>
                  <Link
                    href="/leaderboard/advanced"
                    className="block px-4 py-2 text-xs hover:bg-[#E7E8D1]"
                  >
                    Advanced Leaderboard
                  </Link>
                  <Link
                    href="/moves"
                    className="block px-4 py-2 text-xs hover:bg-[#E7E8D1]"
                  >
                    Moves Rankings
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
              <button className="text-xs font-medium transition-colors hover:underline text-gray-600">
                Team
              </button>
              {teamDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-white border-2 border-black shadow-lg z-10">
                  <Link
                    href="/team-rankings"
                    className="block px-4 py-2 text-xs hover:bg-[#E7E8D1]"
                  >
                    Team Rankings
                  </Link>
                  <Link
                    href="/teams"
                    className="block px-4 py-2 text-xs hover:bg-[#E7E8D1]"
                  >
                    Team Catalog
                  </Link>
                </div>
              )}
            </div>

            <Link
              href="/game"
              className={`text-xs font-medium transition-colors hover:underline ${
                pathname === "/game" ? "text-black" : "text-gray-600"
              }`}
            >
              Game
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
