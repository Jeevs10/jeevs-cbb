import Panel, { PanelHeader } from "@/components/ui/Panel";
import Stat from "@/components/ui/Stat";

function pct(v) {
  return Math.round((v || 0) * 100);
}

export default function PlayerStylePanel({ player }) {
  return (
    <Panel className="mt-6">
      
      <PanelHeader>PLAY STYLE ABILITIES</PanelHeader>

      <div className="space-y-1">
        <Stat
          label="RIM ATTACK"
          value={pct(player.off_style_rim_attack_pct)}
          max={100}
        />

        <Stat
          label="TRANSITION"
          value={pct(player.off_style_transition_pct)}
          max={100}
        />

        <Stat
          label="3PT SNIPER"
          value={pct(player.off_style_perimeter_sniper_pct)}
          max={100}
        />

        <Stat
          label="PnR PLAYMAKER"
          value={pct(player.off_style_pnr_passer_pct)}
          max={100}
        />

        <Stat
          label="POST USAGE"
          value={pct(player.off_style_post_up_pct)}
          max={100}
        />

        <Stat
          label="MID RANGE"
          value={pct(player.off_style_mid_range_pct)}
          max={100}
        />
      </div>
      
    </Panel>
  );
}