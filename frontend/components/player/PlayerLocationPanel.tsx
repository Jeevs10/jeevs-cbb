import TeamLocationMap from "../team/TeamLocationMap";

interface PlayerLocationPanelProps {
  city?: string;
  state?: string;
  primaryColor?: string;
}

export default function PlayerLocationPanel({ city, state, primaryColor }: PlayerLocationPanelProps) {
  if (!city || !state) {
    return null;
  }

  return (
    <div className="border-2 border-black bg-[#C7D0B8] text-black p-3 font-mono">
      <div className="border-b-2 border-black mb-2 pb-1 text-xs font-bold uppercase tracking-wide">
        HOMETOWN
      </div>
      <TeamLocationMap city={city} state={state} primaryColor={primaryColor} />
    </div>
  );
}
