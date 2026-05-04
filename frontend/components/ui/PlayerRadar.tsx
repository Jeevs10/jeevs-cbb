"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

export default function PlayerRadar({ data = [] }: { data: any[] }) {
  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer>
        <RadarChart data={data}>
          <PolarGrid radialLines={true} />
          <PolarRadiusAxis domain={[0, 1]} tickCount={5} />

          <PolarAngleAxis
            dataKey="stat"
            tick={{ fontSize: 11, fill: "#111" }}
          />

          <Radar
            dataKey="value"
            stroke="#111"
            strokeWidth={2.5}
            fill="#111"
            fillOpacity={0.08}
            dot={{ r: 3, fill: "#111" }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}