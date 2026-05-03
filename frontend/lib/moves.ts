type Move = {
  name: string;
  efficiency: number;
  usage: number;        // raw %
  frequencyPctile: number;  // 👈 NEW
  category: string;
};

function safe(v: any) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function makeMove(
  name: string,
  player: any,
  key: string,
  category: string,
  pctileKey: string
): Move {
  return {
    name,
    efficiency: safe(player[`${key}_ppp`]),
    usage: safe(player[`${key}_pct`]),
    frequencyPctile: safe(player[pctileKey]),
    category,
  };
}

export function getPlayerMoves(player: any): Move[] {
  const moves: Move[] = [
    makeMove(
  "Rim Attack",
  player,
  "off_style_rim_attack",
  "finishing",
  "pctile_off_style_rim_attack_pct"
),

makeMove(
  "Sniper",
  player,
  "off_style_perimeter_sniper",
  "shooting",
  "pctile_off_style_perimeter_sniper_pct"
),

makeMove(
  "Mid-Range Assassin",
  player,
  "off_style_mid_range",
  "shooting",
  "pctile_off_style_mid_range_pct"
),

makeMove(
  "Transition Bolt",
  player,
  "off_style_transition",
  "finishing",
  "pctile_off_style_transition_pct"
),

makeMove(
  "PnR Maestro",
  player,
  "off_style_pnr_passer",
  "playmaking",
  "pctile_off_style_pnr_passer_pct"
),

makeMove(
  "Post Dominator",
  player,
  "off_style_post_up",
  "interior",
  "pctile_off_style_post_up_pct"
),
  ];

  return moves
    .filter(m => m.usage > 0.01) // remove noise
    .sort((a, b) => b.efficiency * b.usage - a.efficiency * a.usage)
    .slice(0, 6); // top moves only
}