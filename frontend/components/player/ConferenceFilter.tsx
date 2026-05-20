"use client";

interface ConferenceFilterProps {
  conferenceFilter: "all" | "d1" | "high_major" | string;
  onConferenceChange: (filter: "all" | "d1" | "high_major" | string) => void;
}

export function ConferenceFilter({ conferenceFilter, onConferenceChange }: ConferenceFilterProps) {
  return (
    <div className="mb-3">
      <label className="text-xs font-bold mb-1 block">CONFERENCE</label>
      <select
        value={conferenceFilter}
        onChange={(e) => onConferenceChange(e.target.value)}
        className="w-full px-2 border border-black bg-[#E7E8D1] text-xs font-mono"
      >
        <option value="all">ALL</option>
        <option value="d1">D1</option>
        <option value="high_major">HIGH MAJOR</option>
        <optgroup label="Conferences">
          <option value="ACC">ACC</option>
          <option value="SEC">SEC</option>
          <option value="Big 12">Big 12</option>
          <option value="Big 10">Big 10</option>
          <option value="Big East">Big East</option>
          <option value="AAC">AAC</option>
          <option value="A-10">A-10</option>
          <option value="Mountain West">Mountain West</option>
          <option value="MVC">MVC</option>
          <option value="WCC">WCC</option>
          <option value="Pac-12">Pac-12</option>
          <option value="Big Ten">Big Ten</option>
          <option value="Big East">Big East</option>
          <option value="American">American</option>
          <option value="Atlantic 10">Atlantic 10</option>
          <option value="Conference USA">Conference USA</option>
          <option value="MAC">MAC</option>
          <option value="Missouri Valley">Missouri Valley</option>
          <option value="Mountain West">Mountain West</option>
          <option value="West Coast">West Coast</option>
        </optgroup>
      </select>
    </div>
  );
}
