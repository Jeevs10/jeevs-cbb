"use client";

import Link from "next/link";

export default function PlayerEvolutionPanel({ data, player }) {
  if (!data || !player) return null;

  const {
    player_tier,
    bench_unit = [],
    rotation_piece = [],
    starter = [],
    all_conference = [],
    all_american = [],
  } = data;

  const pick = (arr) => arr?.[0];

  const tiers = [
    { key: "bench_unit", label: "BENCH UNIT", data: pick(bench_unit) },
    { key: "rotation_piece", label: "ROTATION PIECE", data: pick(rotation_piece) },
    { key: "starter", label: "STARTER", data: pick(starter) },
    { key: "all_conference", label: "ALL-CONFERENCE", data: pick(all_conference) },
    { key: "all_american", label: "ALL-AMERICAN", data: pick(all_american) },
  ];

  // -------------------------
  // NAME
  // -------------------------
  const getDisplayName = (p, isCurrent = false) => {
    const rawName = isCurrent ? player?.player_name : p?.player_name;

    if (rawName && rawName !== "NaN" && rawName.trim() !== "") {
      return rawName;
    }

    const code = isCurrent ? player?.player_code : p?.player_code;
    if (!code) return "—";

    return code.replace(/([a-z])([A-Z])/g, "$1 $2");
  };

  // -------------------------
  // META
  // -------------------------
  const getMeta = (p, isCurrent = false) => {
    const team = isCurrent ? player?.team : p?.team;
    const pos = isCurrent ? player?.posClass : p?.posClass || "—";

    if (!team && !pos) return null;

    return [team, pos].filter(Boolean).join(" • ");
  };

  // -------------------------
  // CARD
  // -------------------------
  const Card = ({ p, isCurrent = false }) => {
    return (
      <div
        className={`
          border border-black p-2 text-[10px] w-full transition
          bg-[#E7E8D1]
          ${isCurrent ? "ring-2 ring-black" : "hover:bg-[#dfe3cd]"}
        `}
      >
        <div className="font-bold">
          {getDisplayName(p, isCurrent)}
        </div>

        {getMeta(p, isCurrent) && (
          <div className="opacity-70 text-[9px]">
            {getMeta(p, isCurrent)}
          </div>
        )}

        {!isCurrent && p && (
          <>
            {/* 🔥 FIXED: show percentile instead of raw impact */}
            <div className="opacity-70">
              RAPM Pct: {p.rapm_pct != null ? (p.rapm_pct * 100).toFixed(1) : "—"}
            </div>

            <div className="opacity-50">
              {p.year ?? ""}
            </div>
          </>
        )}

        {isCurrent && (
          <div className="text-[9px] opacity-70 mt-1">
            CURRENT PLAYER
          </div>
        )}
      </div>
    );
  };

  // -------------------------
  // NODE
  // -------------------------
  const Node = ({ label, playerObj, tierKey }) => {
    const isCurrent = tierKey === player_tier;

    return (
      <div className="flex flex-col items-center flex-1">
        <div className="text-[10px] font-bold mb-1">{label}</div>

        {isCurrent ? (
          <Card p={player} isCurrent />
        ) : playerObj ? (
          <Link href={`/player/${playerObj.player_code}`} className="w-full">
            <Card p={playerObj} />
          </Link>
        ) : (
          <div className="border border-dashed border-black p-2 text-[10px] opacity-40 w-full bg-[#E7E8D1]">
            None
          </div>
        )}
      </div>
    );
  };

  // -------------------------
  // RENDER
  // -------------------------
  return (
    <div className="border-2 border-black bg-[#C7D0B8] p-3 space-y-3 text-xs">

      <div className="font-bold border-b border-black pb-1">
        EVOLUTION PATH
      </div>

      <div className="text-[10px]">
        Current Tier: <span className="font-bold">{player_tier}</span>
      </div>

      {/* EVOLUTION LINE */}
      <div className="flex items-center justify-between gap-2 overflow-x-auto">

        {tiers.map((t, idx) => (
          <div key={t.key} className="flex items-center gap-2 flex-1 min-w-[120px]">
            <Node
              label={t.label}
              playerObj={t.data}
              tierKey={t.key}
            />

            {idx < tiers.length - 1 && (
              <div className="text-lg font-bold opacity-70">→</div>
            )}
          </div>
        ))}

      </div>
    </div>
  );
}