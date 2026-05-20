"use client";

import Link from "next/link";
import { Header } from "@/components/ui/Header";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header title="Player Stats Database" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            College Basketball Player Database
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Explore comprehensive player statistics including basic metrics and advanced RAPM analysis.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-8 rounded-lg shadow-lg border border-black">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                All Players
              </h2>
              <p className="text-gray-600 mb-4">
                View all players with fundamental statistics including points, rebounds, assists, and more.
              </p>
              <Link
                href="/leaderboard/basic"
                className="inline-flex items-center px-6 py-3 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] text-base font-medium text-white transition-colors"
              >
                View All Players
              </Link>
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-lg border border-black">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Basic Leaderboard
              </h2>
              <p className="text-gray-600 mb-4">
                View all players with fundamental statistics including points, rebounds, assists, and more.
              </p>
              <Link
                href="/leaderboard/basic"
                className="inline-flex items-center px-6 py-3 border border-black bg-[#E7E8D1] hover:bg-[#dfe2c6] text-base font-medium text-white transition-colors"
              >
                View Basic Stats
              </Link>
            </div>
          </div>
          
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Additional Features
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-lg shadow border border-black">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Player Evolution
                </h3>
                <p className="text-gray-600">
                  Compare players across different RAPM tiers and find similar players at each skill level.
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow border border-black">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Player Profiles
                </h3>
                <p className="text-gray-600">
                  Detailed player statistics, career progression, and advanced analytics.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}