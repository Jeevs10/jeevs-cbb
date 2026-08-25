import { badgeIcons } from "@/lib/badgeIcons";

export default function Badge({
  children,
  level,
  variant = "default",
  name,
}) {
  const levelStyles = {
    1: "bg-[#E7E8D1] text-black",
    2: "bg-[#C7D0B8] text-black",
    3: "bg-[#B8C0A8] text-black",
    4: "bg-[#A8B098] text-black",
    5: "bg-[#98A088] text-black",
  };

  const levelLabels = {
    1: "Basic",
    2: "Advanced",
    3: "Elite",
    4: "Legendary",
    5: "Mythic",
  };

  const variantStyles = {
    default: "bg-[#E7E8D1] text-black border-2 border-black shadow-[3px_3px_0px_black]",
    offense: "bg-[#E7E8D1] text-black border-2 border-black shadow-[3px_3px_0px_black]",
    defense: "bg-[#E7E8D1] text-black border-2 border-black shadow-[3px_3px_0px_black]",
    meta: "bg-[#E7E8D1] text-black border-2 border-black shadow-[3px_3px_0px_black]",
  };

  const Icon = badgeIcons[children];

  if (level) {
    const safeLevel = Math.min(Math.max(level, 1), 5);

    return (
      <div
        className={`flex items-center gap-1 px-2 py-1 text-xs font-mono border-2 border-black shadow-[3px_3px_0px_black] ${levelStyles[safeLevel]}`}
      >
        {Icon && <Icon size={12} />}
        <span>{children}</span>
        <span className="text-black">• {levelLabels[safeLevel]}</span>
      </div>
    );
  }

  return (
    <div
      className={`px-2 py-1 text-xs font-mono border-2 border-black ${variantStyles[variant]}`}
    >
      {children}
    </div>
  );
}