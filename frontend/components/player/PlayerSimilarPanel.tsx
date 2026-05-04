"use client";

import Link from "next/link";

export default function PlayerSimilarPanel({
  player,
  similar,
  styleWeight,
  setStyleWeight,
}) {
  const combined = similar?.combined ?? [];

  return (
    <div className="border-2 border-black bg-[#C7D0B8] p-3 space-y-2 max-h-[420px] overflow-y-auto">

      <div className="text-xs font-bold border-b border-black pb-1">
        SIMILAR PLAYERS
      </div>

      {/* SLIDER */}
      <div className="text-[10px] mb-2">
        <div className="font-bold mb-1">Impact ↔ Style Balance</div>

        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={styleWeight}
          onChange={(e) => setStyleWeight(Number(e.target.value))}
          className="w-full"
        />

        <div className="flex justify-between text-[9px] opacity-70">
          <span>Impact</span>
          <span>Style</span>
        </div>
      </div>

      {/* EMPTY STATE (IMPORTANT DEBUG FIX) */}
      {combined.length === 0 && (
        <div className="text-xs opacity-70">
          No similar players found.
        </div>
      )}

      {/* LIST */}
      {combined.map((p) => (
        <Link
          key={p.player_code}
          href={`/player/${p.player_code}`}
          className="block"
        >
          <div className="flex justify-between items-start text-xs border border-black p-2 bg-[#E7E8D1] hover:bg-[#dfe3cd] transition">

            <div>
              <div className="font-bold">
                {p.player_name ?? p.player_code}
              </div>

              <div className="text-[10px] opacity-70">
                {p.team ?? "—"} • {p.pos ?? "—"} • {p.year ?? "—"}
              </div>

              <div className="mt-1 text-[9px] opacity-80">
                <div className="font-bold">Similarity signals:</div>

                {Array.isArray(p.reasons) && p.reasons.length > 0 ? (
                  p.reasons.slice(0, 3).map((r, i) => (
                    <div key={i}>
                      • {r.feature}: diff {r.delta?.toFixed?.(2) ?? ""}
                    </div>
                  ))
                ) : (
                  <div>• stylistic + impact similarity</div>
                )}
              </div>
            </div>

            <div className="text-right font-bold">
              {((p.similarity ?? 0) * 100).toFixed(1)}%
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}