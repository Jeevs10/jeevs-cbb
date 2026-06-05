"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef } from "react";

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [playerDropdownOpen, setPlayerDropdownOpen] = useState(false);
  const [teamDropdownOpen, setTeamDropdownOpen] = useState(false);
  const [projectionsDropdownOpen, setProjectionsDropdownOpen] = useState(false);
  const [clustersDropdownOpen, setClustersDropdownOpen] = useState(false);
  const playerTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const teamTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const projectionsTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const clustersTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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

  const handleClustersMouseEnter = () => {
    if (clustersTimeoutRef.current) {
      clearTimeout(clustersTimeoutRef.current);
      clustersTimeoutRef.current = null;
    }
    setClustersDropdownOpen(true);
  };

  const handleClustersMouseLeave = () => {
    clustersTimeoutRef.current = setTimeout(() => {
      setClustersDropdownOpen(false);
    }, 200);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="border-b-2 border-black bg-[#C7D0B8]">
      <div className="px-2 sm:px-4">
        <div className="flex justify-between items-center h-12">
          {/* Logo/Title */}
          <Link href="/" className="text-xs sm:text-sm font-bold text-black hover:underline uppercase tracking-wide">
            PORTALMANIA
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="sm:hidden text-black font-bold text-xs border-2 border-black px-2 py-1 bg-[#E7E8D1]"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden sm:flex space-x-4 sm:space-x-6 items-center">
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

            {/* Game */}
            <div
              className="relative"
              onMouseEnter={() => {}}
              onMouseLeave={() => {}}
            >
              <button
                onClick={() => window.location.href = '/game'}
                className="text-xs font-medium transition-colors hover:underline text-black"
              >
                PORTALMANIA
              </button>
              <div className="absolute top-full left-0 mt-1 bg-[#E7E8D1] border-2 border-black shadow-[3px_3px_0px_black] z-10 hidden">
                <Link
                  href="/game"
                  className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                >
                  PORTALMANIA
                </Link>
              </div>
            </div>

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

            {/* Clusters Dropdown */}
            <div
              className="relative"
              onMouseEnter={handleClustersMouseEnter}
              onMouseLeave={handleClustersMouseLeave}
            >
              <button className="text-xs font-medium transition-colors hover:underline text-black">
                Clusters
              </button>
              {clustersDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 bg-[#E7E8D1] border-2 border-black shadow-[3px_3px_0px_black] z-10">
                  <Link
                    href="/clusters"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Cluster Analysis
                  </Link>
                  <Link
                    href="/clusters/leaderboard"
                    className="block px-4 py-2 text-xs hover:bg-[#B8C0A8]"
                  >
                    Cluster Leaderboard
                  </Link>
                </div>
              )}
            </div>
          </nav>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="sm:hidden py-2 border-t-2 border-black">
            <div className="flex flex-col space-y-2">
              <Link
                href="/leaderboard/basic"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Basic Leaderboard
              </Link>
              <Link
                href="/leaderboard/advanced"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Advanced Leaderboard
              </Link>
              <Link
                href="/moves"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Moves Rankings
              </Link>
              <Link
                href="/similarity"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Similarity Map
              </Link>
              <Link
                href="/team-rankings"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Team Rankings
              </Link>
              <Link
                href="/teams"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Team Catalog
              </Link>
              <Link
                href="/game"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                PORTALMANIA
              </Link>
              <Link
                href="/projections/2027"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                2027 Projections
              </Link>
              <Link
                href="/projections/leaderboard"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Projection Leaderboard
              </Link>
              <Link
                href="/clusters"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Cluster Analysis
              </Link>
              <Link
                href="/clusters/leaderboard"
                className="block px-2 py-2 text-xs hover:bg-[#B8C0A8]"
                onClick={() => setMobileMenuOpen(false)}
              >
                Cluster Leaderboard
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
