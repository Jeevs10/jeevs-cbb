import { useEffect, useState } from "react";
import Panel, { PanelHeader } from "@/components/ui/Panel";
import Badge from "@/components/ui/Badge";
import { fetchPlayerBadges } from "@/lib/api";
import { classMap, posMap } from "@/lib/positionLabels";
import { yearClassMap } from "@/lib/yearClassMap";

function formatHeight(h?: string) {
  if (!h) return "—";

  const parts = h.split("-");
  if (parts.length !== 2) return h;

  const feet = parts[0];
  const inches = String(Number(parts[1]));

  return `${feet}'${inches}"`;
}

export default function PlayerHeader({ player }) {
  const [badges, setBadges] = useState<any[]>([]);

  const playerCode = player?.player_code;

  useEffect(() => {
    if (!playerCode) return;

    fetchPlayerBadges(playerCode)
      .then(setBadges)
      .catch(console.error);
  }, [playerCode]);

  return (
    <Panel className="relative overflow-hidden mb-6">

      <div className="absolute inset-0 opacity-10 bg-black" />

      <div className="relative space-y-2">

        <PanelHeader>PLAYER SCOUTING REPORT</PanelHeader>

        <h1 className="text-2xl font-bold text-black">
          {player.player_name}
        </h1>

        {/* TEAM + YEAR */}
        <div className="text-xs text-black/70">
          {player.team} • {player.conf} • {" "}
          {player.is_career
            ? "Career"
            : player.year}
        </div>

        {/* CORE INFO BADGES */}
        <div className="flex gap-2 flex-wrap mt-2">

          <Badge variant="meta">
            CLASS: {classMap[player.roster?.pos] ?? "—"}
          </Badge>

          <Badge variant="meta">
            HT: {formatHeight(player.roster?.height)}
          </Badge>

          <Badge variant="meta">
            POS: {posMap[player.posClass] ?? "—"}
          </Badge>

          {/* 🔥 NEW: YEAR CLASS */}
          <Badge variant="meta">
            YEAR: {player.is_career
              ? "Career"
              : yearClassMap[player.roster?.year_class] ?? "—"}
          </Badge>

        </div>

        {/* ❌ REMOVED: skill badges from header */}

      </div>
    </Panel>
  );
}