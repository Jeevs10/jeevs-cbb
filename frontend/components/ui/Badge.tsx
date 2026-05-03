import { badgeIcons } from "@/lib/badgeIcons";

export default function Badge({
  children,
  level,
  variant = "default",
  name,
}) {
  const levelStyles = {
    1: "bg-gray-200 text-gray-800",
    2: "bg-green-200 text-green-900",
    3: "bg-blue-200 text-blue-900",
    4: "bg-purple-300 text-purple-900",
    5: "bg-yellow-300 text-yellow-900",
  };

  const levelLabels = {
    1: "Basic",
    2: "Advanced",
    3: "Elite",
    4: "Legendary",
    5: "Mythic",
  };

    const variantStyles = {
      default: "bg-white text-black",
      offense: "bg-red-100 text-red-900 border-red-300",
      defense: "bg-blue-100 text-blue-900 border-blue-300",
      meta: "bg-[#e7e8d1] text-black border-black shadow-[2px_2px_0px_black]",
    };

  // 🧠 detect icon
  const Icon = badgeIcons[children];

  // ✅ Skill badge (with level)
  if (level) {
    const safeLevel = Math.min(Math.max(level, 1), 5);

    return (
      <div
        className={`flex items-center gap-1 px-2 py-1 text-xs font-mono border border-black shadow-[2px_2px_0px_black] ${levelStyles[safeLevel]}`}
      >
        {Icon && <Icon size={12} />}
        <span>{children}</span>
        <span className="opacity-60">• {levelLabels[safeLevel]}</span>
      </div>
    );
  }

  // ✅ Meta badge (no level)
  return (
    <div
      className={`px-2 py-1 text-xs font-mono border border-black ${variantStyles[variant]}`}
    >
      {children}
    </div>
  );
}