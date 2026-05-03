export default function StatBar({ label, value = 0, max = 100 }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className="flex items-center justify-between text-xs py-1 border-b border-gray-700">
      {/* label */}
      <span className="text-gray-300 w-24">{label}</span>

      {/* bar container */}
      <div className="flex-1 mx-2 h-2 bg-gray-800 border border-gray-600 relative">
        <div
          style={{ width: `${pct}%` }}
          className="h-full bg-green-400"
        />
      </div>

      {/* value */}
      <span className="text-gray-200 w-10 text-right">
        {value?.toFixed?.(0) ?? value}
      </span>
    </div>
  );
}