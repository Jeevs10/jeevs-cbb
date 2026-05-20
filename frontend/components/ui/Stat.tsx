// components/ui/Stat.tsx
export default function Stat({ label, value, max = 100 }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className="flex items-center justify-between text-xs py-1 border-b border-black/30">
      <span className="w-24 text-black/70">{label}</span>

      <div className="flex-1 mx-2 h-2 bg-black/10 border border-black relative">
        <div
          style={{ width: `${pct}%` }}
          className="h-full bg-black"
        />
      </div>

      <span className="w-10 text-right font-bold">
        {typeof value === "number" ? value.toFixed(0) : value}
      </span>
    </div>
  );
}