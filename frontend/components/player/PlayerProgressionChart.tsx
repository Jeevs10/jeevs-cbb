"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Panel from "@/components/ui/Panel";
import { PanelHeader } from "@/components/ui/Panel";

type PlayerProgressionChartProps = {
  playerHistory: any[];
  dataTier: "basic" | "enriched";
};

// Color palette for consistent styling
const COLORS = [
  "#000000", // black
  "#3B82F6", // blue
  "#EF4444", // red
  "#10B981", // green
  "#F59E0B", // amber
  "#8B5CF6", // purple
  "#EC4899", // pink
  "#06B6D4", // cyan
];

// Available fields for basic players
const BASIC_FIELDS = [
  { key: "PPG", label: "PPG", category: "per_game" },
  { key: "APG", label: "APG", category: "per_game" },
  { key: "RPG", label: "RPG", category: "per_game" },
  { key: "SPG", label: "SPG", category: "per_game" },
  { key: "BPG", label: "BPG", category: "per_game" },
  { key: "MPG", label: "MPG", category: "per_game" },
  { key: "TrueShootingPct", label: "TS%", category: "percentages" },
  { key: "OffensiveRating", label: "Off RTG", category: "ratings" },
  { key: "DefensiveRating", label: "Def RTG", category: "ratings" },
  { key: "NetRating", label: "Net RTG", category: "ratings" },
];

// Available fields for enriched players
const ENRICHED_FIELDS = [
  ...BASIC_FIELDS,
  { key: "adj_rapm_margin", label: "RAPM", category: "ratings" },
  { key: "off_usage", label: "Usage", category: "ratings" },
  { key: "off_efg", label: "eFG%", category: "percentages" },
  { key: "off_assist", label: "AST%", category: "percentages" },
];

export default function PlayerProgressionChart({
  playerHistory,
  dataTier,
}: PlayerProgressionChartProps) {
  const [selectedFields, setSelectedFields] = useState<string[]>(["PPG", "RPG", "APG"]);

  const availableFields =
    dataTier === "basic" ? BASIC_FIELDS : ENRICHED_FIELDS;

  // Prepare data for the chart
  const chartData = playerHistory
    .map((year) => {
      const games = Math.max(year.Games || 1, 1);
      const data: any = { year: year.year };
      
      selectedFields.forEach((field) => {
        // Handle both camelCase and space-separated field names
        let value = year[field] ?? year[field.replace(/ /g, "_")] ?? year[field.replace(/_/g, " ")] ?? 0;
        
        // Calculate per-game stats from totals if not available
        if (value === 0 || value === null || value === undefined) {
          if (field === "PPG" && year.Points) {
            value = year.Points / games;
          } else if (field === "APG" && year.Assists) {
            value = year.Assists / games;
          } else if (field === "RPG" && year["Rebounds Total"]) {
            value = year["Rebounds Total"] / games;
          } else if (field === "SPG" && year.Steals) {
            value = year.Steals / games;
          } else if (field === "BPG" && year.Blocks) {
            value = year.Blocks / games;
          } else if (field === "MPG" && year.Minutes) {
            value = year.Minutes / games;
          } else if (field === "ORB_PG" && year["Rebounds Offensive"]) {
            value = year["Rebounds Offensive"] / games;
          } else if (field === "DRB_PG" && year["Rebounds Defensive"]) {
            value = year["Rebounds Defensive"] / games;
          }
        }
        
        data[field] = value;
      });
      
      return data;
    })
    .sort((a, b) => a.year - b.year);

  const toggleField = (field: string) => {
    setSelectedFields((prev) =>
      prev.includes(field)
        ? prev.filter((f) => f !== field)
        : [...prev, field]
    );
  };

  // Get field category
  const getFieldCategory = (field: string) => {
    const fieldDef = availableFields.find((f) => f.key === field);
    return fieldDef?.category || "per_game";
  };

  // Get color for field based on index
  const getFieldColor = (index: number) => COLORS[index % COLORS.length];

  if (chartData.length === 0) {
    return (
      <Panel>
        <PanelHeader>PLAYER PROGRESSION</PanelHeader>
        <div className="p-4 text-center text-gray-600">
          <p className="text-sm">No progression data available</p>
        </div>
      </Panel>
    );
  }

  return (
    <Panel>
      <PanelHeader>PLAYER PROGRESSION</PanelHeader>

      {/* Field Selection */}
      <div className="p-3 border-b border-black">
        <p className="text-xs font-bold mb-2">Select fields to display:</p>
        <div className="flex flex-wrap gap-2">
          {availableFields.map((field, index) => (
            <button
              key={field.key}
              onClick={() => toggleField(field.key)}
              className={`px-2 py-1 text-[10px] border border-black font-mono transition-all
                ${selectedFields.includes(field.key)
                  ? "bg-black text-white"
                  : "bg-white text-black hover:bg-gray-100"
                }`}
              style={{
                borderColor: selectedFields.includes(field.key) 
                  ? getFieldColor(index) 
                  : undefined
              }}
            >
              {field.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="p-4">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
            <XAxis 
              dataKey="year" 
              stroke="#000"
              fontSize={12}
              tick={{ fontSize: 11 }}
            />
            <YAxis 
              yAxisId="left"
              stroke="#000"
              fontSize={12}
              tick={{ fontSize: 11 }}
              label={{ value: 'Per Game', angle: -90, position: 'insideLeft', fontSize: 10 }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#000"
              fontSize={12}
              tick={{ fontSize: 11 }}
              label={{ value: 'Ratings / %', angle: 90, position: 'insideRight', fontSize: 10 }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #000',
                borderRadius: '4px',
                fontSize: '11px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '11px' }}
              iconType="circle"
            />
            {selectedFields.map((field, index) => {
              const category = getFieldCategory(field);
              const isLeftAxis = category === "per_game" || category === "totals";
              const yAxisId = isLeftAxis ? "left" : "right";
              
              return (
                <Line
                  key={field}
                  type="monotone"
                  dataKey={field}
                  yAxisId={yAxisId}
                  stroke={getFieldColor(index)}
                  strokeWidth={2}
                  dot={{ r: 4, fill: getFieldColor(index), strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                  name={availableFields.find((f) => f.key === field)?.label || field}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
