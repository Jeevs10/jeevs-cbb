export default function StatBar({ label, value = 0, max = 100, rank = null }: { label: string; value?: number; max?: number; rank?: number | null | undefined }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className="flex items-center justify-between text-xs py-1 border-b border-black">
      
      {/* label */}
      <span className="text-black w-24">{label}</span>

      {/* bar container */}
      <div className="flex-1 mx-2 h-2 bg-[#E7E8D1] border border-black relative">
        <div
          style={{ width: `${pct}%` }}
          className="h-full bg-black"
        />
      </div>

      {/* value and rank */}
      <div className="flex items-center gap-2 text-right">
        <span className="text-black w-10">
          {value?.toFixed?.(0) ?? value}
        </span>
        {rank !== null && rank !== 0 && (
          <span className="text-[10px] text-gray-600 w-8">
            #{rank.toFixed(0)}
          </span>
        )}
      </div>
    </div>
  );
}