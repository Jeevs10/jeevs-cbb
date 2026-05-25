"use client";

import { useState, useEffect } from "react";
import { TEAM_COLORS } from '@/app/game/teamColors';

const METRICS = [
  { value: "rapm", label: "RAPM" },
  { value: "bpm", label: "BPM" },
  { value: "vorp", label: "VORP" },
  { value: "combined", label: "Combined" },
];

export default function PlayerEvolutionPanel({ data, player, onMetricChange }: any) {
  if (!data || !player) return null;

  const [metric, setMetric] = useState("rapm");
  const [currentTierIndex, setCurrentTierIndex] = useState(0);

  const {
    player_tier,
    bench_unit = [],
    rotation_piece = [],
    starter = [],
    all_conference = [],
    all_american = [],
  } = data;

  const handleMetricChange = (newMetric: string) => {
    setMetric(newMetric);
    if (onMetricChange) {
      onMetricChange(newMetric);
    }
  };

  const pick = (arr: any[]) => arr?.[0];

  const tiers = [
    { key: "bench_unit", label: "Bench Unit", data: pick(bench_unit), stage: 1 },
    { key: "rotation_piece", label: "Rotation", data: pick(rotation_piece), stage: 2 },
    { key: "starter", label: "Starter", data: pick(starter), stage: 3 },
    { key: "all_conference", label: "All-Conf", data: pick(all_conference), stage: 4 },
    { key: "all_american", label: "All-American", data: pick(all_american), stage: 5 },
  ];

  // Initialize current tier index based on player's actual tier
  useEffect(() => {
    const currentPlayerTierIndex = tiers.findIndex(t => t.key === player_tier);
    if (currentPlayerTierIndex >= 0) {
      setCurrentTierIndex(currentPlayerTierIndex);
    }
  }, [player_tier]);

  const currentTier = tiers[currentTierIndex];
  const canEvolve = currentTierIndex < tiers.length - 1 && tiers[currentTierIndex + 1].data;
  const canDevolve = currentTierIndex > 0;

  const handleEvolve = () => {
    if (!canEvolve) return;
    setCurrentTierIndex(currentTierIndex + 1);
  };

  const handleDevolve = () => {
    if (!canDevolve) return;
    setCurrentTierIndex(currentTierIndex - 1);
  };

  // -------------------------
  // NAME
  // -------------------------
  const getDisplayName = (p, isCurrent = false) => {
    const rawName = isCurrent ? player?.player_name : p?.player_name;

    if (rawName && rawName !== "NaN" && rawName.trim() !== "") {
      return rawName;
    }

    const code = isCurrent ? player?.AthleteSourceId : p?.AthleteSourceId;
    if (!code) return "—";

    return code.replace(/([a-z])([A-Z])/g, "$1 $2");
  };

  // -------------------------
  // META
  // -------------------------
  const getMeta = (p, isCurrent = false) => {
    const team = isCurrent ? player?.team : p?.team;
    const pos = isCurrent ? player?.pos : p?.pos;

    if (!team && !pos) return null;

    return [team, pos].filter(Boolean).join(" • ");
  };

  // -------------------------
  // CARD
  // -------------------------
  const Card = ({ p, tierKey, isSelected, showCurrentPlayer, onClick }: any) => {
    const playerToShow = showCurrentPlayer ? player : p;
    const teamColor = playerToShow?.team ? TEAM_COLORS[playerToShow.team] || { primary: '#1a1a1a', secondary: '#4a4a4a' } : { primary: '#1a1a1a', secondary: '#4a4a4a' };
    
    const getMetricLabel = () => {
      if (metric === "rapm") return "RAPM";
      if (metric === "bpm") return "BPM";
      if (metric === "vorp") return "VORP";
      if (metric === "combined") return "Impact";
      return "RAPM";
    };

    const getMetricValue = (playerData: any) => {
      if (metric === "rapm") return playerData?.rapm_pct || playerData?.rapm;
      if (metric === "bpm") return playerData?.bpm_pct || playerData?.bpm;
      if (metric === "vorp") return playerData?.vorp_pct || playerData?.vorp;
      if (metric === "combined") {
        const rapm = playerData?.rapm_pct || playerData?.rapm || 0;
        const bpm = playerData?.bpm_pct || playerData?.bpm || 0;
        const vorp = playerData?.vorp_pct || playerData?.vorp || 0;
        return (rapm + bpm + vorp) / 3;
      }
      return playerData?.rapm_pct || playerData?.rapm;
    };

    return (
      <div
        onClick={onClick}
        className={`
          relative border-4 p-2 text-[9px] w-32 h-44 transition-all duration-300 flex-shrink-0 cursor-pointer
          ${isSelected ? 'border-black scale-110' : 'border-gray-400'}
          bg-white rounded-lg shadow-[4px_4px_0px_black]
        `}
      >
        {/* Card header with team color */}
        <div
          className="text-white p-1 text-center rounded-t"
          style={{ backgroundColor: teamColor.primary }}
        >
          <div className="text-[8px] font-bold tracking-wider truncate">
            {getDisplayName(playerToShow, showCurrentPlayer)}
          </div>
        </div>

        {/* Card content */}
        <div className="p-2 flex flex-col items-center text-center bg-white">
          {getMeta(playerToShow, showCurrentPlayer) && (
            <div className="text-[8px] mb-1 text-gray-700">
              {getMeta(playerToShow, showCurrentPlayer)}
            </div>
          )}

          {playerToShow && (
            <>
              <div className="flex items-center gap-1 mb-1">
                <span className="text-[7px] text-gray-600">{getMetricLabel()}:</span>
                <span className="text-[9px] font-bold" style={{ color: teamColor.primary }}>
                  {getMetricValue(playerToShow) != null ? (getMetricValue(playerToShow) * 100).toFixed(1) : "—"}
                </span>
              </div>

              <div className="text-[7px] text-gray-500">
                {playerToShow.year ?? ""}
              </div>

              {/* Additional stats for selected card */}
              {isSelected && (
                <div className="mt-1 pt-1 border-t border-gray-300 w-full">
                  <div className="text-[6px] text-gray-600">
                    {playerToShow.pts && <div>PTS: {playerToShow.pts.toFixed(1)}</div>}
                    {playerToShow.ast && <div>AST: {playerToShow.ast.toFixed(1)}</div>}
                    {playerToShow.reb && <div>REB: {playerToShow.reb.toFixed(1)}</div>}
                  </div>
                </div>
              )}

              {showCurrentPlayer && (
                <div className="mt-1 pt-1 border-t-2 border-black text-[7px] font-bold">
                  CURRENT
                </div>
              )}
            </>
          )}
        </div>

        {/* Card footer with team secondary color */}
        <div
          className="absolute bottom-0 left-0 right-0 h-1.5 rounded-b"
          style={{ backgroundColor: teamColor.secondary }}
        ></div>

        {/* Stage badge */}
        <div className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black text-white text-[7px] font-bold flex items-center justify-center border-2 border-white">
          {tiers.find(t => t.key === tierKey)?.stage}
        </div>
      </div>
    );
  };

  // -------------------------
  // RENDER
  // -------------------------
  return (
    <div className="border-2 border-black bg-[#c7d0b8] p-6 space-y-4 text-xs">

      <div className="flex items-center justify-between border-b-2 border-black pb-2">
        <div className="font-bold text-sm">EVOLUTION PATH</div>
        <div className="text-[9px]">
          Stage: <span className="font-bold">{currentTier.label}</span>
        </div>
      </div>

      {/* METRIC SELECTOR */}
      <div className="flex items-center gap-2">
        <label className="text-[10px] font-bold">Metric:</label>
        <select
          value={metric}
          onChange={(e) => handleMetricChange(e.target.value)}
          className="px-2 py-1 border-2 border-black bg-[#e7e8d1] text-[10px]"
        >
          {METRICS.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      </div>

      {/* TRADING CARD DISPLAY */}
      <div className="flex flex-col items-center gap-4 py-6">
        
        {/* All 5 cards in a row */}
        <div className="flex items-center justify-center gap-1 overflow-x-auto pb-4 px-8 pt-6">
          {tiers.map((t, idx) => {
            const isSelected = idx === currentTierIndex;
            const isCurrentPlayerTier = t.key === player_tier;
            const scaleClass = isSelected ? 'scale-110' : 'scale-75 opacity-60';
            const zIndex = isSelected ? 'z-10' : 'z-0';
            const handleCardClick = () => {
              setCurrentTierIndex(idx);
            };
            
            return (
              <div
                key={t.key}
                className={`transition-all duration-500 ease-in-out ${scaleClass} ${zIndex}`}
              >
                {isCurrentPlayerTier ? (
                  <Card p={player} tierKey={t.key} isSelected={isSelected} showCurrentPlayer={true} onClick={handleCardClick} />
                ) : t.data ? (
                  <Card p={t.data} tierKey={t.key} isSelected={isSelected} showCurrentPlayer={false} onClick={handleCardClick} />
                ) : (
                  <div className="w-32 h-44 border-4 border-dashed border-black bg-[#e7e8d1] rounded-lg flex flex-col items-center justify-center flex-shrink-0">
                    <div className="text-xl mb-1">?</div>
                    <div className="text-[8px]">No data</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Evolution Controls */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleDevolve}
            disabled={!canDevolve}
            className="px-4 py-2 border-2 border-black bg-[#e7e8d1] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#dfe3cd]"
          >
            ← Devolve
          </button>

          <button
            onClick={handleEvolve}
            disabled={!canEvolve}
            className="px-4 py-2 border-2 border-black bg-[#c7d0b8] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#b8c0a8] font-bold"
          >
            Evolve →
          </button>
        </div>

        {/* Stage indicator */}
        <div className="flex gap-2">
          {tiers.map((t, idx) => (
            <div
              key={t.key}
              className={`w-3 h-3 rounded-full border-2 border-black cursor-pointer transition-all ${
                idx === currentTierIndex ? 'bg-black scale-125' : 'bg-white hover:bg-gray-300'
              }`}
              onClick={() => setCurrentTierIndex(idx)}
            />
          ))}
        </div>

      </div>
    </div>
  );
}