"use client";

import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from "recharts";

interface ProjectionYear {
  year: number;
  projected_bpm?: number;
  bpm_change?: number;
  confidence_interval?: [number, number];
  percentile_rank?: number;
  sample_size?: number;
  error?: string;
}

interface HistoricalBpmData {
  year: number;
  BPM: number | null;
  Name: string;
  Team: string;
}

interface PlayerProjectionGraphProps {
  currentBpm: number;
  currentYear: number;
  projections: ProjectionYear[];
  historicalBpm?: HistoricalBpmData[] | null;
}

export default function PlayerProjectionGraph({ currentBpm, currentYear, projections, historicalBpm }: PlayerProjectionGraphProps) {
  // Prepare data for the chart - include all historical BPM if available
  const historicalData = historicalBpm
    ?.filter((h) => h.BPM !== null)
    .map((h) => ({
      year: h.year,
      bpm: h.BPM,
      type: h.year === currentYear ? "Current" : "Historical",
    })) || [];

  // Add current year if not already in historical data
  const hasCurrentYear = historicalData.some((h) => h.year === currentYear);
  const currentYearData = hasCurrentYear ? [] : [{
    year: currentYear,
    bpm: currentBpm,
    type: "Current",
  }];

  const chartData = [
    ...historicalData,
    ...currentYearData,
    ...projections
      .filter((p) => !p.error && p.projected_bpm !== undefined)
      .map((p) => ({
        year: p.year,
        bpm: p.projected_bpm,
        lower: p.confidence_interval?.[0],
        upper: p.confidence_interval?.[1],
        type: "Projected",
      })),
  ];

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No projection data available
      </div>
    );
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="year"
            stroke="#6b7280"
            tick={{ fill: "#6b7280" }}
          />
          <YAxis
            stroke="#6b7280"
            tick={{ fill: "#6b7280" }}
            label={{ value: "BPM", angle: -90, position: "insideLeft", fill: "#6b7280" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            }}
            formatter={(value: any, name?: any) => {
              if (value === undefined || value === null) return [value, name];
              const nameStr = String(name || "");
              if (nameStr === "bpm") return [Number(value).toFixed(2), "BPM"];
              if (nameStr === "lower") return [Number(value).toFixed(2), "Lower Bound"];
              if (nameStr === "upper") return [Number(value).toFixed(2), "Upper Bound"];
              return [value, name];
            }}
          />
          <Legend />

          {/* Confidence interval area */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="#3b82f6"
            strokeOpacity={0.3}
            fill="#3b82f6"
            fillOpacity={0.1}
            name="95% Confidence Interval"
            hide
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="#3b82f6"
            strokeOpacity={0.3}
            fill="#3b82f6"
            fillOpacity={0.1}
            name="95% Confidence Interval"
            hide
          />

          {/* Main projection line */}
          <Line
            type="monotone"
            dataKey="bpm"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: "#3b82f6", strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7 }}
            name="BPM"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Custom confidence interval visualization */}
      {projections.some((p) => p.confidence_interval) && (
        <div className="mt-4 space-y-2">
          {projections
            .filter((p) => !p.error && p.confidence_interval)
            .map((p) => (
              <div key={p.year} className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{p.year} Projection:</span>
                <div className="flex items-center gap-4">
                  <span className="text-gray-500">
                    {p.confidence_interval![0].toFixed(1)} - {p.confidence_interval![1].toFixed(1)}
                  </span>
                  <span className="font-semibold text-blue-600">
                    {p.projected_bpm?.toFixed(2)} BPM
                  </span>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
