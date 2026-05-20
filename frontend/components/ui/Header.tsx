"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface HeaderProps {
  title?: string;
}

export function Header({ title = "Player Stats Database" }: HeaderProps) {
  const pathname = usePathname();
  
  // Debug logging to understand navigation behavior
  console.log('Header - pathname:', pathname, 'title:', title);
  
  // Check if we're on a leaderboard page and if "All Players" is selected
  const isLeaderboardPage = pathname.startsWith('/leaderboard');
  const isAllPlayersSelected = pathname === '/leaderboard/basic' || 
    (pathname === '/' && title === 'Player Stats Database');
  
  console.log('Header - isLeaderboardPage:', isLeaderboardPage, 'isAllPlayersSelected:', isAllPlayersSelected);
  
  return (
    <header className="border-b border-black bg-[#C7D0B8] shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Title */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-black">
              {title}
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex space-x-8">
            <Link
              href="/"
              className={`text-sm font-medium transition-colors hover:text-blue-600 ${
                pathname === "/" ? "text-black" : "text-gray-600"
              }`}
            >
              Home
            </Link>
            <Link
              href="/leaderboard/basic"
              className={`text-sm font-medium transition-colors hover:text-blue-600 ${
                isAllPlayersSelected ? "text-black" : "text-gray-600"
              }`}
            >
              Basic Leaderboard
              {isAllPlayersSelected && (
                <span className="ml-2 text-xs text-gray-600">(All Players)</span>
              )}
            </Link>
            <Link
              href="/leaderboard/advanced"
              className={`text-sm font-medium transition-colors hover:text-blue-600 ${
                pathname === "/leaderboard/advanced" ? "text-black" : "text-gray-600"
              }`}
            >
              Advanced Leaderboard
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
