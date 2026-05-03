"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

const safe = (v) => {
  const num = Number(v);
  return Number.isFinite(num) ? num : 0;
};

export default function PlayerRadar({ player }) {
  // --- SCORING ---
  const scoring =
    0.75 * safe(player.pctile_off_adj_rtg) +
    0.25 * safe(player.pctile_off_usage);

  // --- PLAYMAKING ---
  const playmaking =
    0.6 * safe(player.pctile_off_assist) +
    0.25 * safe(player.pctile_off_ast_rim) +
    0.15 * (1 - safe(player.pctile_off_to));

  // --- DEFENSE ---
  const defense =
    0.4 * safe(player.pctile_def_adj_rapm) +
    0.3 * safe(player.pctile_def_stl) +
    0.3 * safe(player.pctile_def_blk);

  // --- REBOUNDING ---
  const rebounding =
    0.6 * safe(1- player.pctile_def_reb) +
    0.4 * safe(player.pctile_off_reb);

  const clamp = (x) => Math.max(0, Math.min(1, x));

  const data = [
  { stat: "SCORING", value: clamp(scoring) },
  { stat: "PLAYMAKING", value: clamp(playmaking) },
  { stat: "DEFENSE", value: clamp(defense) },
  { stat: "REBOUNDING", value: clamp(rebounding) },
  ];
  console.log("RADAR COMPONENT DATA:", 1- player.pctile_def_reb, player.pctile_off_reb);

  console.log("OVERALL RADAR:", {
  scoring,
  playmaking,
  defense,
  rebounding,
  });

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