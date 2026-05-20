"use client";

function getGrade(eff: number) {
  if (eff > 1.1) return "S";
  if (eff > 1.0) return "A";
  if (eff > 0.9) return "B";
  return "C";
}

export default function PlayerMovesPanel({ moves = [] }) {
  return (
    <div className="border-2 border-black bg-[#C7D0B8] p-3 space-y-2">
      
      <div className="text-xs font-bold border-b border-black pb-1">
        MOVES SET
      </div>

      {moves.length === 0 && (
        <div className="text-xs opacity-70">No moves found.</div>
      )}

      {moves.map((m, i) => (
        <div
          key={i}
          className="flex justify-between items-center text-xs border border-black p-2 bg-[#E7E8D1]"
        >
          <div>
            <div className="font-bold">{m.name}</div>

            <div className="text-[10px] opacity-70">
              Usage: {(m.usage * 100).toFixed(1)}%
            </div>

            <div className="text-[10px] opacity-90">
              League Freq: {(m.frequencyPctile * 100).toFixed(0)}th %
            </div>

            <div className="w-full h-1 bg-black/20 mt-1">
              <div
                className="h-1 bg-black"
                style={{ width: `${m.frequencyPctile * 100}%` }}
              />
            </div>
          </div>

          <div className="text-right">
            <div className="font-bold">{m.efficiency.toFixed(2)} PPP</div>
            <div className="text-[10px]">
              Grade: {getGrade(m.efficiency)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}