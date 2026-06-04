"use client";

import { useState, useEffect } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
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
  perGame: "Per Game",
  custom: "Custom",
};

const AVAILABLE_FIELDS = [
  "PPG", "RPG", "APG", "SPG", "BPG", "MPG",
  "FG%", "3P%", "FT%", "TS%", "eFG%",
  "TO%", "AST%", "USG%", "ORB%", "DRB%"
];

const PERCENTAGE_FIELDS = [
  "off_assist", "off_to", "off_usage", "off_efg", "off_ftr",
  "off_threep", "off_twop", "off_twopmid", "off_twoprim",
  "off_orb", "def_orb", "off_reb", "def_reb",
  "def_stl", "def_blk", "def_fc"
];

export default function PlayerRadar({ playerId, year }: PlayerRadarProps) {
  const [activePreset, setActivePreset] = useState<string>("overview");
  const [statMode, setStatMode] = useState<"perGame" | "percentage">("percentage");
  const [customFields, setCustomFields] = useState<string[]>(["off_assist", "off_twop", "off_orb"]);
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

  const handlePresetChange = (preset: string) => {
    setActivePreset(preset);
    // Set statMode based on preset
    if (preset === "perGame") {
      setStatMode("perGame");
      setCustomFields(["PPG", "RPG", "APG"]);
    } else {
      setStatMode("percentage");
      setCustomFields(["off_assist", "off_twop", "off_orb"]);
    }
  };

  const TabButton = ({ id, label }: { id: string; label: string }) => (
    <button
      onClick={() => handlePresetChange(id)}
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
            {(statMode === "perGame" ? AVAILABLE_FIELDS : PERCENTAGE_FIELDS).map((field) => (
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
              <Tooltip
                formatter={(value: any, name: any, props: any) => {
                  const rawValue = props.payload?.raw || value;
                  if (typeof rawValue === 'number') {
                    return [rawValue.toFixed(3), name];
                  }
                  return [rawValue, name];
                }}
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid black",
                  borderRadius: "4px",
                  fontSize: "12px",
                  fontFamily: "monospace",
                }}
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