"use client";

import Link from "next/link";
import Panel from "@/components/ui/Panel";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#E7E8D1]">
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-2xl font-bold text-black mb-4 uppercase tracking-wide">
            CBB Stats
          </h1>
          <p className="text-xs text-black mb-8 max-w-2xl mx-auto">
            College basketball analytics with Pokemon-style player cards. Explore player stats, clusters, and projections.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-12">
          <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
            <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
                All Players
              </h2>
            <p className="text-xs text-black mb-4">
              Browse the complete player database with fundamental statistics.
              </p>
              <Link
                href="/leaderboard/basic"
              className="inline-block px-4 py-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] text-xs font-bold text-black uppercase tracking-wide"
              >
              View Players
              </Link>
          </Panel>
          
          <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
            <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
              Advanced Leaderboard
              </h2>
            <p className="text-xs text-black mb-4">
              RAPM analysis and advanced metrics for deeper evaluation.
              </p>
              <Link
              href="/leaderboard/advanced"
              className="inline-block px-4 py-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] text-xs font-bold text-black uppercase tracking-wide"
              >
              View Advanced
              </Link>
          </Panel>

          <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
            <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
                Teams
              </h2>
            <p className="text-xs text-black mb-4">
              Team analytics, rosters, and performance statistics.
              </p>
              <Link
                href="/teams"
              className="inline-block px-4 py-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] text-xs font-bold text-black uppercase tracking-wide"
              >
                View Teams
              </Link>
          </Panel>
          </div>
          
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xs font-bold text-black mb-6 uppercase tracking-wide">
              Additional Features
            </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
              <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
                Similarity Map
              </h3>
              <p className="text-xs text-black">
                Find players with similar playing styles and statistical profiles.
              </p>
            </Panel>
            
            <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
              <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
                2027 Projections
              </h3>
              <p className="text-xs text-black">
                Cluster-based player projections for next season.
              </p>
            </Panel>

            <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
              <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
                Cluster Analysis
                </h3>
              <p className="text-xs text-black">
                Explore player archetypes and cluster compositions.
              </p>
            </Panel>

            <Panel className="hover:bg-[#B8C0A8] transition cursor-pointer">
              <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
                Moves Rankings
                </h3>
              <p className="text-xs text-black">
                Player efficiency by offensive move type.
                </p>
            </Panel>
          </div>
        </div>
      </main>
    </div>
  );
}