
type Badge = {
  name: string;
  level: number;
  category?: "scoring" | "defense" | "playmaking" | "hustle";
};

function getLevel(pct: number) {
  if (pct > 0.97) return 5; // Mythic
  if (pct > 0.92) return 4; // Legendary
  if (pct > 0.85) return 3; // Elite
  if (pct > 0.75) return 2; // Advanced
  if (pct > 0.65) return 1; // Basic
  return 0;
}

export function getPlayerBadges(player: any) {
  if (!player) return []; // ✅ HARD GUARD

  const safe = (v: any) => {
    const num = Number(v);
    return Number.isFinite(num) ? num : 0;
  };

  const badges = [];

  // 🏹 SNIPER
  const sniperScore = Math.min(
    safe(player.pctile_off_threep),
    safe(player.pctile_off_style_perimeter_sniper_ppp)
  );

  const sniperLevel = getLevel(sniperScore);
  if (sniperLevel > 0) {
    badges.push({
      name: "Sniper",
      level: sniperLevel,
      category: "scoring",
    });
  }

  // 🗡 MID RANGE
  const midScore = Math.min(
    safe(player.pctile_off_style_mid_range_usg),
    safe(player.pctile_off_style_mid_range_ppp)
  );

  const midLevel = getLevel(midScore);
  if (midLevel > 0) {
    badges.push({
      name: "Mid-Range Assassin",
      level: midLevel,
      category: "scoring",
    });
  }

  // 💥 RIM PRESSURE
  const rimScore = Math.min(
    safe(player.pctile_off_style_rim_attack_usg),
    safe(player.pctile_off_style_rim_attack_ppp)
  );

  const rimLevel = getLevel(rimScore);
  if (rimLevel > 0) {
    badges.push({
      name: "Rim Breaker",
      level: rimLevel,
      category: "scoring",
    });
  }

  // 🎯 PLAYMAKING
  const playmakingScore = Math.min(
    safe(player.pctile_off_assist),
    1 - safe(player.pctile_off_to)
  );

  const playLevel = getLevel(playmakingScore);
  if (playLevel > 0) {
    badges.push({
      name: "Floor General",
      level: playLevel,
      category: "playmaking",
    });
  }

  // 🧱 DEFENSE
  const defenseScore = safe(player.pctile_def_adj_rapm);
  const defenseLevel = getLevel(defenseScore);

  if (defenseLevel > 0) {
    badges.push({
      name: "Defensive Anchor",
      level: defenseLevel,
      category: "defense",
    });
  }

  // 🛑 SHOT BLOCKING
  const blockLevel = getLevel(safe(player.pctile_def_blk));
  if (blockLevel > 0) {
    badges.push({
      name: "Rim Protector",
      level: blockLevel,
      category: "defense",
    });
  }

  // 🧲 REBOUNDING
  const rebLevel = getLevel(safe(player.pctile_def_reb));
  if (rebLevel > 0) {
    badges.push({
      name: "Glass Cleaner",
      level: rebLevel,
      category: "hustle",
    });
  }

  // ⚡ TRANSITION
  const transLevel = getLevel(
    safe(player.pctile_off_style_transition_usg)
  );

  if (transLevel > 0) {
    badges.push({
      name: "Fast Break Finisher",
      level: transLevel,
      category: "scoring",
    });
  }

  // Sort by strongest
  return badges
    .sort((a, b) => b.level - a.level)
    .slice(0, 8);
}