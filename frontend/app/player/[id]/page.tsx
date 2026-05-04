"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import {
  fetchPlayer,
  fetchPlayerMoves,
  fetchSimilarPlayers,
  fetchPlayerBadges,
  fetchPlayerRadar,
} from "@/lib/api";

import { useYear } from "@/app/context/YearContext";

import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";
import PlayerRadar from "@/components/ui/PlayerRadar";

import Stat from "@/components/ui/Stat";
import PlayerHeader from "@/components/player/PlayerHeader";
import Badge from "@/components/ui/Badge";
import PlayerMovesPanel from "@/components/player/PlayerMovesPanel";
import PlayerSimilarPanel from "@/components/player/PlayerSimilarPanel";

import YearToggle from "@/components/ui/YearToggle";

export default function PlayerPage() {
  const { id } = useParams();
  const { year } = useYear();

  const [player, setPlayer] = useState<any>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [radar, setRadar] = useState<any[]>([]);
  const [badges, setBadges] = useState<any[]>([]);
  const [moves, setMoves] = useState<any[]>([]);
  const [similar, setSimilar] = useState<any>(null);
  const [styleWeight, setStyleWeight] = useState(0.7);

  const playerCode = player?.player_code;

  // -------------------------
  // PLAYER
  // -------------------------
  useEffect(() => {
    if (!id) return;

    fetchPlayer(id, year)
      .then((data) => {
        setPlayer(data.player);
        setAvailableYears(data.available_years || []);
      })
      .catch(console.error);
  }, [id, year]);

  // -------------------------
  // RADAR (🔥 FIXED)
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerRadar(playerCode, year)
      .then(setRadar)
      .catch(console.error);
  }, [playerCode, year]);

  // -------------------------
  // MOVES
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerMoves(playerCode, year)
      .then(setMoves)
      .catch(console.error);
  }, [playerCode, year]);

  // -------------------------
  // BADGES
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerBadges(playerCode, year)
      .then(setBadges)
      .catch(console.error);
  }, [playerCode, year]);

  // -------------------------
  // SIMILAR
  // -------------------------
  useEffect(() => {
    if (!playerCode) return;

    fetchSimilarPlayers(playerCode, styleWeight, year)
      .then(setSimilar)
      .catch(console.error);
  }, [playerCode, styleWeight, year]);

  if (!player) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#E7E8D1] text-black font-mono">
        LOADING PLAYER DATA...
      </div>
    );
  }

  return (
    <div className="p-3 space-y-6">

      <PlayerHeader player={player} />

      {/* YEAR TOGGLE */}
      {availableYears.length > 0 && (
        <YearToggle availableYears={availableYears} />
      )}

      <div className="text-xs font-bold">
        Viewing: {year ?? "Latest Season"}
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        <Panel>
          <PanelHeader>BASE STATS</PanelHeader>

          <Stat label="OFF RTG" value={player.off_rtg} max={140} />
          <Stat label="DEF RTG (inverse)" value={150 - player.def_rtg} max={150} />
          <Stat label="USAGE" value={player.off_usage * 100} max={50} />
          <Stat label="RAPM" value={player.adj_rapm_margin} max={20} />
        </Panel>

        <Panel>
          <PanelHeader>ADVANCED PROFILE</PanelHeader>

          {/* 🔥 FIXED: use radar API instead of player object */}
          <PlayerRadar data={radar} />
        </Panel>
      </div>

      {/* BADGES */}
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

      {/* MOVES */}
      <Panel>
        <PanelHeader>MOVES</PanelHeader>

        <PlayerMovesPanel moves={moves} />
      </Panel>

      {/* SIMILAR */}
      <Panel>
        <PanelHeader>SIMILAR PLAYERS</PanelHeader>

        <PlayerSimilarPanel
          player={player}
          similar={similar}
          styleWeight={styleWeight}
          setStyleWeight={setStyleWeight}
        />
      </Panel>

    </div>
  );
}