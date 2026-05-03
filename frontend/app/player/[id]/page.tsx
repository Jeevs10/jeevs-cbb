"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { fetchPlayer } from "../../../lib/api";

import Panel, { PanelDark } from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";
import PlayerRadar from "@/components/ui/PlayerRadar";

import Stat from "@/components/ui/Stat";
import PlayerHeader from "@/components/player/PlayerHeader";
import PlayerStylePanel from "@/components/player/PlayerStylePanel";
import { getPlayerBadges } from "../../../lib/badges";
import Badge from "@/components/ui/Badge";
import PlayerMovesPanel from "@/components/player/PlayerMovesPanel";


export default function PlayerPage() {
  const { id } = useParams();
  const [player, setPlayer] = useState(null);
  

  useEffect(() => {
    if (!id) return;
    fetchPlayer(id).then(setPlayer);
  }, [id]);

  if (!player) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING PLAYER DATA...
      </div>
    );
  }
  const badges = getPlayerBadges(player);

  return (
    <div className="p-3 space-y-6">
      {/* CRT overlay (kept as global effect layer) */}
      <div className="pointer-events-none fixed inset-0 opacity-10 bg-[radial-gradient(circle,rgba(0,0,0,0.15)_1px,transparent_1px)] [background-size:4px_4px]" />

      {/* PLAYER HEADER (already good, leave as-is or later convert to Card) */}
      <PlayerHeader player={player} />

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* BASE STATS PANEL */}
        <Panel>
          <PanelHeader>BASE STATS</PanelHeader>

          <Stat label="OFF RTG" value={player.off_rtg} max={140} />
          <Stat label="DEF RTG (inverse)" value={150 - player.def_rtg} max={150} />
          <Stat label="USAGE" value={player.off_usage * 100} max={50} />
          <Stat label="RAPM" value={player.adj_rapm_margin} max={20} />
        </Panel>

        {/* ADVANCED PROFILE PANEL (now properly systemized) */}
        <Panel>
  <PanelHeader>ADVANCED PROFILE</PanelHeader>
    
  <PlayerRadar player={player} />
</Panel>
      </div>
    {/* ✅ ADD THIS HERE */}
    <Panel>
  <PanelHeader>PLAYER BADGES</PanelHeader>

  <div className="flex flex-wrap gap-2">
    {badges.map((b, i) => (
      <Badge key={i} level={b.level} name={b.name}>
        {b.name}
      </Badge>
    ))}
  </div>
</Panel>
<Panel>
  <PanelHeader>MOVES</PanelHeader>
  <PlayerMovesPanel player={player} />
</Panel>

      {/* STYLE / ARCHETYPE PANEL */}
      <Panel>
        <PanelHeader>PLAYSTYLE ANALYSIS</PanelHeader>
        <PlayerStylePanel player={player} />
      </Panel>
    </div>
  );

}