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
    <div className="space-y-2">

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

      {/* SCROLL AREA */}
      <div className="max-h-[320px] overflow-y-auto pr-1 space-y-2">

        {/* EMPTY */}
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

              {/* LEFT */}
              <div className="flex-1 pr-2">

                <div className="font-bold">
                  {p.player_name ?? p.player_code}
                </div>

                <div className="text-[10px] opacity-70">
                  {p.team ?? "—"} • {p.pos ?? "—"} • {p.year ?? "—"}
                </div>

                <div className="mt-2 grid grid-cols-2 gap-3 text-[9px]">

                  {/* WHY SIMILAR */}
                  <div>
                    <div className="font-bold mb-1">Why similar</div>

                    {p.reasons?.length > 0 ? (
                      p.reasons.slice(0, 3).map((r, i) => (
                        <div key={i}>• {r.feature}</div>
                      ))
                    ) : (
                      <div>• stylistic + impact similarity</div>
                    )}
                  </div>

                  {/* DIFFERENCES */}
                  <div>
                    <div className="font-bold mb-1">Key differences</div>

                    {p.differences?.length > 0 ? (
                      p.differences.slice(0, 3).map((d, i) => (
                        <div key={i}>• {d.feature}</div>
                      ))
                    ) : (
                      <div>• minimal differences</div>
                    )}
                  </div>

                </div>
              </div>

              {/* RIGHT */}
              <div className="text-right font-bold w-16">
                {((p.similarity ?? 0) * 100).toFixed(1)}%
              </div>

            </div>
          </Link>
        ))}

      </div>
    </div>
  );
}