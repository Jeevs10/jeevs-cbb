"use client";

import { useState } from "react";
import StatBar from "@/components/ui/StatBar";

function safe(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

function perGame(value, games) {
  const g = Math.max(safe(games), 1);
  return safe(value) / g;
}

export default function PlayerStatsPanel({ player }) {
  const [tab, setTab] = useState("overview");

  const isBasicPlayer = player?.data_tier === "basic";
  const isCareer = player?.is_career === true;

  const games = safe(player.Games);

  // For career mode, use pre-calculated per-game stats from backend
  // For single year mode, calculate from total stats
  const min_pg = isCareer ? safe(player.MPG) : perGame(player.Minutes, games);
  const pts_pg = isCareer ? safe(player.PPG) : perGame(player.Points, games);
  const ast_pg = isCareer ? safe(player.APG) : perGame(player.Assists, games);
  const reb_pg = isCareer ? safe(player.RPG) : perGame(player["Rebounds Total"], games);
  const orb_pg = isCareer ? safe(player.ORB_PG) : perGame(player["Rebounds Offensive"], games);
  const drb_pg = isCareer ? safe(player.DRB_PG) : perGame(player["Rebounds Defensive"], games);
  const stl_pg = isCareer ? safe(player.SPG) : perGame(player.Steals, games);
  const blk_pg = isCareer ? safe(player.BPG) : perGame(player.Blocks, games);

  const TabButton = ({ id, label }) => (
    <button
      onClick={() => setTab(id)}
      className={`px-2 py-1 text-[10px] border border-black uppercase font-mono
        ${tab === id ? "bg-black text-white" : "bg-[#D7DFC8] text-black"}
      `}
    >
      {label}
    </button>
  );

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 space-y-3 font-mono">

      {/* ---------------- TABS ---------------- */}
      <div className="flex flex-wrap gap-1 border-b border-black pb-2 text-black">
        <TabButton id="overview" label="OVERVIEW" />
        {!isBasicPlayer && <TabButton id="impact" label="IMPACT" />}
        {!isBasicPlayer && <TabButton id="role" label="ROLE" />}
        {!isBasicPlayer && <TabButton id="scoring" label="SCORING" />}
        {!isBasicPlayer && <TabButton id="defense" label="DEFENSE" />}
        {!isBasicPlayer && <TabButton id="rebounding" label="REBOUND" />}
      </div>

      {/* ---------------- OVERVIEW ---------------- */}
      {tab === "overview" && (
        <div className="space-y-2 text-black">
          <StatBar label="MPG" value={min_pg} max={40} />
          <StatBar label="PPG" value={pts_pg} max={30} />
          <StatBar label="APG" value={ast_pg} max={10} />
          <StatBar label="RPG" value={reb_pg} max={12} />
          <StatBar label="SPG" value={stl_pg} max={3} />
          <StatBar label="BPG" value={blk_pg} max={3} />
          <StatBar label="BPM" value={safe(player.BPM)} max={15} />
          <StatBar label="VORP" value={safe(player.VORP)} max={15} />
          <StatBar label="GAMES" value={games} max={35} />
        </div>
      )}

      {/* ---------------- IMPACT ---------------- */}
      {tab === "impact" && !isBasicPlayer && (
        <div className="space-y-2 text-black">
          <StatBar label="OFF RTG" value={player.off_rtg} max={130} />
          <StatBar label="DEF RTG" value={150 - player.def_rtg} max={100} />
          <StatBar label="NET RTG" value={player.NetRating} max={20} />
          <StatBar label="RAPM" value={player.adj_rapm_margin} max={10} />
          <StatBar label="BPM" value={safe(player.BPM)} max={15} />
          <StatBar label="PROD" value={player.adj_prod_margin} max={10} />
        </div>
      )}

      {/* ---------------- ROLE ---------------- */}
      {tab === "role" && !isBasicPlayer && (
        <div className="space-y-2 text-black">
          <StatBar label="USAGE" value={player.Usage} max={40} />
          <StatBar label="ASSIST %" value={player.off_assist * 100} max={50} />
          <StatBar label="TO %" value={player.off_to * 100} max={30} />
          <StatBar label="TEAM POSSESS %" value={player.off_team_poss_pct * 100} max={100} />
        </div>
      )}

      {/* ---------------- SCORING ---------------- */}
      {tab === "scoring" && (
        <div className="space-y-2 text-black">
          <StatBar label="eFG%" value={player.off_efg * 100 || player.EffectiveFieldGoalPct * 100} max={70} />
          <StatBar label="TS%" value={player.TrueShootingPct * 100} max={70} />
          <StatBar label="FTR" value={player.off_ftr * 100 || player.FreeThrowRate * 100} max={60} />
          <StatBar label="FT%" value={player["FreeThrows Pct"] > 1 ? player["FreeThrows Pct"] : player["FreeThrows Pct"] * 100} max={100} />
          {isBasicPlayer && (
            <>
              <StatBar label="2P%" value={player["TwoPointFieldGoals Pct"] * 100} max={70} />
              <StatBar label="3P%" value={player["ThreePointFieldGoals Pct"] * 100} max={50} />
            </>
          )}
        </div>
      )}

      
      {/* ---------------- DEFENSE ---------------- */}
      {tab === "defense" && (
        <div className="space-y-2 text-black">
          <StatBar label="STOCKS PG" value={stl_pg + blk_pg} max={5} />
          <StatBar label="STEALS PG" value={stl_pg} max={3} />
          <StatBar label="BLOCKS PG" value={blk_pg} max={3} />
          <StatBar label="DEF RTG" value={player.def_rtg || player.DefensiveRating} max={120} />
        </div>
      )}

      {/* ---------------- REBOUNDING ---------------- */}
      {tab === "rebounding" && (
        <div className="space-y-2 text-black">
          <StatBar label="OREB" value={orb_pg} max={5} />
          <StatBar label="DREB" value={drb_pg} max={8} />
          <StatBar label="REB" value={reb_pg} max={12} />
        </div>
      )}

      {/* ---------------- EFFICIENCY (Basic only) ---------------- */}
      {tab === "efficiency" && isBasicPlayer && (
        <div className="space-y-2 text-black">
          <StatBar label="OFF RTG" value={player.OffensiveRating} max={130} />
          <StatBar label="NET RTG" value={player.NetRating} max={20} />
          <StatBar label="BPM" value={safe(player.BPM)} max={15} />
          <StatBar label="USAGE" value={player.Usage} max={40} />
          <StatBar label="AST/TO" value={player.AssistsTurnoverRatio} max={5} />
          <StatBar label="PORPAG" value={player.PORPAG} max={5} />
        </div>
      )}

      
    </div>
  );
}