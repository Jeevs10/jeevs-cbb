import StatBar from "@/components/ui/StatBar";
export default function PlayerStatsPanel({ player }) {
  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-3">
      
      {/* section header */}
      <div className="text-xs font-bold border-b border-black pb-1 mb-2">
        BASE STATS
      </div>

      <StatBar label="OFF" value={player.off_rtg} max={140} />
      <StatBar label="DEF" value={150 - player.def_rtg} max={100} />
      <StatBar label="USG" value={player.off_usage * 100} max={40} />
      <StatBar label="RAPM" value={player.adj_rapm_margin} max={10} />

    </div>
  );
}