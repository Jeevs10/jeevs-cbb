"use client";

interface Move {
  name: string;
  usage: number;
  frequencyPctile: number;
  efficiency: number;
  efficiencyPctile?: number;
}

function getGrade(efficiencyPercentile: number, frequencyPercentile: number) {
  // Combine percentiles to get overall percentile
  // Weight efficiency more heavily than frequency (70% efficiency, 30% frequency)
  const overallPercentile = (efficiencyPercentile * 0.7) + (frequencyPercentile * 0.3);
  
  if (overallPercentile >= 0.90) return "S";
  if (overallPercentile >= 0.88) return "A+";
  if (overallPercentile >= 0.85) return "A";
  if (overallPercentile >= 0.80) return "A-";
  if (overallPercentile >= 0.78) return "B+";
  if (overallPercentile >= 0.75) return "B";
  if (overallPercentile >= 0.70) return "B-";
  if (overallPercentile >= 0.68) return "C+";
  if (overallPercentile >= 0.65) return "C";
  if (overallPercentile >= 0.60) return "C-";
  if (overallPercentile >= 0.58) return "D+";
  if (overallPercentile >= 0.55) return "D";
  if (overallPercentile >= 0.50) return "D-";
  return "F";
}

export default function PlayerMovesPanel({ moves = [] }: { moves: Move[] }) {
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
              Grade: {getGrade(m.efficiencyPctile || 0, m.frequencyPctile)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}