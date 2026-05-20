interface TeamHeaderProps {
  team: {
    primary_color?: string;
    secondary_color?: string;
    display_name?: string;
    school?: string;
    conference?: string;
    current_city?: string;
    current_state?: string;
    mascot?: string;
    current_venue?: string;
  };
}

export default function TeamHeader({ team }: TeamHeaderProps) {
  const primaryColor = team?.primary_color || "#000000";
  const secondaryColor = team?.secondary_color || "#ffffff";

  return (
    <div 
      className="relative overflow-hidden mb-6 border-2 border-black p-4"
      style={{
        backgroundColor: primaryColor,
      }}
    >
      <div className="relative space-y-2">

        <div className="text-xs font-bold" style={{ color: secondaryColor }}>
          TEAM SCOUTING REPORT
        </div>

        <h1 className="text-2xl font-bold" style={{ color: secondaryColor }}>
          {team?.display_name || team?.school}
        </h1>

        {/* CONFERENCE + LOCATION */}
        <div className="text-xs" style={{ color: secondaryColor, opacity: 0.8 }}>
          {team?.conference} • {team?.current_city}, {team?.current_state}
        </div>

        {/* CORE INFO BADGES */}
        <div className="flex gap-2 flex-wrap mt-2">
          <div className="px-2 py-1 text-xs font-mono border border-black bg-[#e7e8d1] text-black shadow-[2px_2px_0px_black]">
            MASCOT: {team?.mascot || "—"}
          </div>

          <div className="px-2 py-1 text-xs font-mono border border-black bg-[#e7e8d1] text-black shadow-[2px_2px_0px_black]">
            VENUE: {team?.current_venue || "—"}
          </div>
        </div>

      </div>
    </div>
  );
}
