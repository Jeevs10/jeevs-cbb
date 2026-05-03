import Panel, { PanelHeader } from "@/components/ui/Panel";
import Badge from "@/components/ui/Badge";
import { getPlayerBadges } from "@/lib/badges";
import { classMap, posMap } from "@/lib/positionLabels";


function formatHeight(h?: string) {
  if (!h) return "—";

  const parts = h.split("-");

  if (parts.length !== 2) return h;

  const feet = parts[0];
  const inches = String(Number(parts[1])); 

  return `${feet}'${inches}"`;
}

export default function PlayerHeader({ player }) {
  const badges = getPlayerBadges(player);
const topBadge = badges[0];
  return (
    <Panel className="relative overflow-hidden mb-6">
      
      {/* subtle background accent (kept but toned down into system style) */}
      <div className="absolute inset-0 opacity-10 bg-black" />

      <div className="relative space-y-2">
        
        <PanelHeader>PLAYER SCOUTING REPORT</PanelHeader>

        <h1 className="text-2xl font-bold text-black">
          {player.player_name}
        </h1>

        <div className="text-xs text-black/70">
          {player.team} • {player.conf} • {player.year}
        </div>
        
        {/* metadata row */}
        <div className="flex gap-2 flex-wrap mt-2">
        <Badge variant="meta">
          CLASS: {classMap[player.roster.pos] ?? "—"}
        </Badge>

        <Badge variant="meta">
          HT: {formatHeight(player.roster.height) ?? "—"}
        </Badge>

        <Badge variant="meta">
          POS: {posMap[player.posClass] ?? "—"}
        </Badge>
      </div>

      </div>
    </Panel>
  );
}