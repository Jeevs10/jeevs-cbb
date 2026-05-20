"use client";

import { useState } from "react";
import StatBar from "@/components/ui/StatBar";

interface TeamAnalyticsPanelProps {
  analytics?: any;
}

function safe(v: any): number {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

interface StatOption {
  id: string;
  label: string;
  valuePath: string;
  rankPath: string;
  max: number;
  isDefense?: boolean;
  isPercentage?: boolean;
  category: "offense" | "defense" | "efficiency";
}

const AVAILABLE_STATS: StatOption[] = [
  // Offense
  { id: "off_adj_ppp", label: "ADJ OFF PPP", valuePath: "off_adj_ppp", rankPath: "rank_off_adj_ppp", max: 140, category: "offense" },
  { id: "off_ppp", label: "OFF PPP", valuePath: "off_ppp", rankPath: "rank_off_ppp", max: 130, category: "offense" },
  { id: "off_efg", label: "OFF EFG", valuePath: "off_efg", rankPath: "rank_off_efg", max: 70, isPercentage: true, category: "offense" },
  { id: "off_to", label: "OFF TO %", valuePath: "off_to", rankPath: "rank_off_to", max: 30, isPercentage: true, category: "offense" },
  { id: "off_ftr", label: "OFF FTR", valuePath: "off_ftr", rankPath: "rank_off_ftr", max: 50, isPercentage: true, category: "offense" },
  { id: "off_orb", label: "OFF ORB %", valuePath: "off_orb", rankPath: "rank_off_orb", max: 50, isPercentage: true, category: "offense" },
  { id: "off_assist", label: "OFF ASSIST %", valuePath: "off_assist", rankPath: "rank_off_assist", max: 80, isPercentage: true, category: "efficiency" },
  { id: "off_threep", label: "OFF 3P %", valuePath: "off_threep", rankPath: "rank_off_threep", max: 50, isPercentage: true, category: "efficiency" },
  { id: "off_twop", label: "OFF 2P %", valuePath: "off_twop", rankPath: "rank_off_twop", max: 70, isPercentage: true, category: "efficiency" },
  // Defense
  { id: "def_adj_ppp", label: "ADJ DEF PPP", valuePath: "def_adj_ppp", rankPath: "rank_def_adj_ppp", max: 140, isDefense: true, category: "defense" },
  { id: "def_ppp", label: "DEF PPP", valuePath: "def_ppp", rankPath: "rank_def_ppp", max: 130, isDefense: true, category: "defense" },
  { id: "def_efg", label: "DEF EFG", valuePath: "def_efg", rankPath: "rank_def_efg", max: 70, isDefense: true, isPercentage: true, category: "defense" },
  { id: "def_to", label: "DEF TO %", valuePath: "def_to", rankPath: "rank_def_to", max: 30, isDefense: true, isPercentage: true, category: "defense" },
  { id: "def_ftr", label: "DEF FTR", valuePath: "def_ftr", rankPath: "rank_def_ftr", max: 50, isDefense: true, isPercentage: true, category: "defense" },
  { id: "def_orb", label: "DEF ORB %", valuePath: "def_orb", rankPath: "rank_def_orb", max: 50, isDefense: true, isPercentage: true, category: "defense" },
  { id: "def_threep", label: "DEF 3P %", valuePath: "def_threep", rankPath: "rank_def_threep", max: 50, isDefense: true, isPercentage: true, category: "efficiency" },
  { id: "def_twop", label: "DEF 2P %", valuePath: "def_twop", rankPath: "rank_def_twop", max: 70, isDefense: true, isPercentage: true, category: "efficiency" },
  // Efficiency
  { id: "tempo", label: "TEMPO", valuePath: "tempo", rankPath: "rank_tempo", max: 80, category: "efficiency" },
];

export default function TeamAnalyticsPanel({ analytics }: TeamAnalyticsPanelProps) {
  const [tab, setTab] = useState("offense");
  const [selectedStats, setSelectedStats] = useState<string[]>([
    "off_adj_ppp", "off_ppp", "off_efg", "def_adj_ppp", "def_ppp", "tempo"
  ]);

  if (!analytics) {
    return (
      <div className="border-2 border-black bg-[#C7D0B8] text-black p-2 font-mono">
        <div className="text-center text-gray-600">
          <p className="text-xs mb-1">Analytics not available</p>
          <p className="text-[10px]">This team does not have advanced analytics data</p>
        </div>
      </div>
    );
  }

  const TabButton = ({ id, label }: { id: string; label: string }) => (
    <button
      onClick={() => setTab(id)}
      className={`px-2 py-1 text-[10px] border border-black uppercase font-mono
        ${tab === id ? "bg-black text-white" : "bg-[#D7DFC8] text-black"}
      `}
    >
      {label}
    </button>
  );

  const toggleStat = (statId: string) => {
    setSelectedStats(prev => 
      prev.includes(statId) 
        ? prev.filter(id => id !== statId)
        : [...prev, statId]
    );
  };

  const getStatValue = (stat: StatOption): number => {
    const value = safe(analytics[stat.valuePath]);
    if (stat.isDefense) {
      return stat.max - value;
    }
    if (stat.isPercentage) {
      return value * 100;
    }
    return value;
  };

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-2 space-y-2 font-mono">

      {/* ---------------- TABS ---------------- */}
      <div className="flex flex-wrap gap-1 border-b border-black pb-2 text-black">
        <TabButton id="offense" label="OFFENSE" />
        <TabButton id="defense" label="DEFENSE" />
        <TabButton id="efficiency" label="EFFICIENCY" />
        <TabButton id="custom" label="CUSTOM" />
      </div>

      {/* ---------------- OFFENSE ---------------- */}
      {tab === "offense" && (
        <div className="space-y-1.5 text-black">
          <StatBar label="ADJ OFF PPP" value={safe(analytics.off_adj_ppp)} max={140} rank={safe(analytics.rank_off_adj_ppp)} />
          <StatBar label="OFF PPP" value={safe(analytics.off_ppp)} max={130} rank={safe(analytics.rank_off_ppp)} />
          <StatBar label="OFF EFG" value={safe(analytics.off_efg) * 100} max={70} rank={safe(analytics.rank_off_efg)} />
          <StatBar label="OFF TO %" value={safe(analytics.off_to) * 100} max={30} rank={safe(analytics.rank_off_to)} />
          <StatBar label="OFF FTR" value={safe(analytics.off_ftr) * 100} max={50} rank={safe(analytics.rank_off_ftr)} />
          <StatBar label="OFF ORB %" value={safe(analytics.off_orb) * 100} max={50} rank={safe(analytics.rank_off_orb)} />
        </div>
      )}

      {/* ---------------- DEFENSE ---------------- */}
      {tab === "defense" && (
        <div className="space-y-1.5 text-black">
          <StatBar label="ADJ DEF PPP" value={140 - safe(analytics.def_adj_ppp)} max={140} rank={safe(analytics.rank_def_adj_ppp)} />
          <StatBar label="DEF PPP" value={130 - safe(analytics.def_ppp)} max={130} rank={safe(analytics.rank_def_ppp)} />
          <StatBar label="DEF EFG" value={100 - safe(analytics.def_efg) * 100} max={70} rank={safe(analytics.rank_def_efg)} />
          <StatBar label="DEF TO %" value={100 - safe(analytics.def_to) * 100} max={30} rank={safe(analytics.rank_def_to)} />
          <StatBar label="DEF FTR" value={100 - safe(analytics.def_ftr) * 100} max={50} rank={safe(analytics.rank_def_ftr)} />
          <StatBar label="DEF ORB %" value={100 - safe(analytics.def_orb) * 100} max={50} rank={safe(analytics.rank_def_orb)} />
        </div>
      )}

      {/* ---------------- EFFICIENCY ---------------- */}
      {tab === "efficiency" && (
        <div className="space-y-1.5 text-black">
          <StatBar label="TEMPO" value={safe(analytics.tempo)} max={80} rank={safe(analytics.rank_tempo)} />
          <StatBar label="OFF ASSIST %" value={safe(analytics.off_assist) * 100} max={80} rank={safe(analytics.rank_off_assist)} />
          <StatBar label="OFF 3P %" value={safe(analytics.off_threep) * 100} max={50} rank={safe(analytics.rank_off_threep)} />
          <StatBar label="OFF 2P %" value={safe(analytics.off_twop) * 100} max={70} rank={safe(analytics.rank_off_twop)} />
          <StatBar label="DEF 3P %" value={100 - safe(analytics.def_threep) * 100} max={50} rank={safe(analytics.rank_def_threep)} />
          <StatBar label="DEF 2P %" value={100 - safe(analytics.def_twop) * 100} max={70} rank={safe(analytics.rank_def_twop)} />
        </div>
      )}

      {/* ---------------- CUSTOM ---------------- */}
      {tab === "custom" && (
        <div className="space-y-2 text-black">
          {/* Stat Selector */}
          <div className="max-h-48 overflow-y-auto border border-black p-2">
            <div className="text-[10px] font-bold border-b border-black pb-1 mb-2">SELECT STATS TO DISPLAY</div>
            {AVAILABLE_STATS.map(stat => (
              <label key={stat.id} className="flex items-center gap-2 text-[10px] cursor-pointer hover:bg-black/5 p-1">
                <input
                  type="checkbox"
                  checked={selectedStats.includes(stat.id)}
                  onChange={() => toggleStat(stat.id)}
                  className="w-3 h-3"
                />
                <span className="uppercase">{stat.label}</span>
              </label>
            ))}
          </div>

          {/* Selected Stats Display */}
          {selectedStats.length > 0 ? (
            <div className="space-y-1.5">
              {selectedStats.map(statId => {
                const stat = AVAILABLE_STATS.find(s => s.id === statId);
                if (!stat) return null;
                return (
                  <StatBar 
                    key={stat.id}
                    label={stat.label}
                    value={getStatValue(stat)}
                    max={stat.max}
                    rank={safe(analytics[stat.rankPath])}
                  />
                );
              })}
            </div>
          ) : (
            <div className="text-[10px] text-gray-600 text-center py-4">
              Select stats to display above
            </div>
          )}
        </div>
      )}

    </div>
  );
}
