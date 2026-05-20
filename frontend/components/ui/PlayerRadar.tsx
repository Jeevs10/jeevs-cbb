"use client";

import { useState, useEffect } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { fetchPlayerRadar } from "@/lib/api";

type PlayerRadarProps = {
  playerId?: string;
  year?: string | number | null;
};

const RADAR_PRESETS = {
  overview: "Overview",
  scoring: "Scoring",
  playmaking: "Playmaking",
  defense: "Defense",
  efficiency: "Efficiency",
  custom: "Custom",
};

const AVAILABLE_FIELDS = [
  "PPG", "RPG", "APG", "SPG", "BPG", "MPG",
  "FG%", "3P%", "FT%", "TS%", "eFG%",
  "TO%", "AST%", "USG%", "ORB%", "DRB%"
];

export default function PlayerRadar({ playerId, year }: PlayerRadarProps) {
  const [activePreset, setActivePreset] = useState<string>("overview");
  const [customFields, setCustomFields] = useState<string[]>(["PPG", "RPG", "APG"]);
  const [radarData, setRadarData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!playerId) return;

    const fetchRadar = async () => {
      setLoading(true);
      try {
        const isCustom = activePreset === "custom";
        const data = await fetchPlayerRadar(
          String(playerId),
          year as any,
          isCustom ? "custom" : activePreset,
          isCustom ? customFields : undefined
        );
        setRadarData(data.error ? [] : data);
      } catch (error) {
        console.error("Failed to fetch radar data:", error);
        setRadarData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRadar();
  }, [playerId, year, activePreset, customFields]);

  const toggleCustomField = (field: string) => {
    setCustomFields((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field]
    );
  };

  const TabButton = ({ id, label }: { id: string; label: string }) => (
    <button
      onClick={() => setActivePreset(id)}
      className={`px-2 py-1 text-[10px] border border-black font-mono
        ${activePreset === id ? "bg-black text-white" : "bg-white text-black hover:bg-gray-100"}
      `}
    >
      {label}
    </button>
  );

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-2 mb-3 flex-wrap">
        {Object.entries(RADAR_PRESETS).map(([key, label]) => (
          <TabButton key={key} id={key} label={label} />
        ))}
      </div>

      {/* Custom Field Selection */}
      {activePreset === "custom" && (
        <div className="mb-3 p-2 border border-black bg-gray-50">
          <p className="text-[10px] font-bold mb-2">SELECT FIELDS:</p>
          <div className="flex flex-wrap gap-1">
            {AVAILABLE_FIELDS.map((field) => (
              <button
                key={field}
                onClick={() => toggleCustomField(field)}
                className={`px-2 py-1 text-[9px] border border-black font-mono
                  ${customFields.includes(field) ? "bg-black text-white" : "bg-white text-black"}
                `}
              >
                {field}
              </button>
            ))}
          </div>
          <p className="text-[9px] text-gray-600 mt-2">
            Selected: {customFields.length > 0 ? customFields.join(", ") : "None"}
          </p>
        </div>
      )}

      {/* Radar Chart */}
      <div className="w-full h-[350px]">
        {loading ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            Loading...
          </div>
        ) : radarData.length > 0 ? (
          <ResponsiveContainer>
            <RadarChart data={radarData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <PolarGrid radialLines={true} stroke="#e5e5e5" />
              <PolarRadiusAxis domain={[0, 1]} tickCount={5} stroke="#000" fontSize={9} />
              <PolarAngleAxis
                dataKey="stat"
                tick={{ fontSize: 10, fill: "#111" }}
                tickLine={{ stroke: "#000" }}
              />
              <Radar
                dataKey="value"
                stroke="#000"
                strokeWidth={2.5}
                fill="#000"
                fillOpacity={0.08}
                dot={{ r: 3, fill: "#000" }}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            {activePreset === "custom" && customFields.length === 0
              ? "Select fields to display"
              : "No radar data available"}
          </div>
        )}
      </div>
    </div>
  );
}