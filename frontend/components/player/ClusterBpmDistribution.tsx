"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from "recharts";

interface ClusterBpmDistributionProps {
  distribution: number[];
  currentBpm: number;
  projectedBpm?: number;
  avgBpm: number;
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p10: number;
  };
}

export default function ClusterBpmDistribution({
  distribution,
  currentBpm,
  projectedBpm,
  avgBpm,
  percentiles,
}: ClusterBpmDistributionProps) {
  // Create histogram bins
  const min = Math.min(...distribution, currentBpm, projectedBpm || currentBpm) - 2;
  const max = Math.max(...distribution, currentBpm, projectedBpm || currentBpm) + 2;
  const binCount = 20;
  const binWidth = (max - min) / binCount;

  const histogramData = Array.from({ length: binCount }, (_, i) => {
    const binStart = min + i * binWidth;
    const binEnd = binStart + binWidth;
    const count = distribution.filter(
      (val) => val >= binStart && val < binEnd
    ).length;
    return {
      bin: `${binStart.toFixed(1)}`,
      count,
      binStart,
      binEnd,
    };
  });

  return (
    <div className="w-full">
      <div className="mb-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Cluster Average BPM:</span>
          <span className="font-semibold">{avgBpm.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Your Current BPM:</span>
          <span className="font-semibold text-blue-600">{currentBpm.toFixed(2)}</span>
        </div>
        {projectedBpm !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Projected BPM:</span>
            <span className="font-semibold text-green-600">{projectedBpm.toFixed(2)}</span>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={histogramData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="bin"
            stroke="#6b7280"
            tick={{ fill: "#6b7280", fontSize: 10 }}
            interval={2}
          />
          <YAxis
            stroke="#6b7280"
            tick={{ fill: "#6b7280" }}
            label={{ value: "Count", angle: -90, position: "insideLeft", fill: "#6b7280", fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            }}
            formatter={(value: any) => [value, "Players"]}
          />
          <Bar dataKey="count" fill="#3b82f6" name="Players" />
          <ReferenceLine x={currentBpm.toFixed(1)} stroke="#2563eb" strokeWidth={2} strokeDasharray="5 5" label="Current" />
          {projectedBpm !== undefined && (
            <ReferenceLine x={projectedBpm.toFixed(1)} stroke="#16a34a" strokeWidth={2} strokeDasharray="5 5" label="Projected" />
          )}
          <ReferenceLine x={avgBpm.toFixed(1)} stroke="#dc2626" strokeWidth={2} strokeDasharray="3 3" label="Avg" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-5 gap-2 text-xs">
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-gray-600">10th</div>
          <div className="font-semibold">{percentiles.p10.toFixed(1)}</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-gray-600">25th</div>
          <div className="font-semibold">{percentiles.p25.toFixed(1)}</div>
        </div>
        <div className="text-center p-2 bg-blue-50 rounded">
          <div className="text-gray-600">50th</div>
          <div className="font-semibold">{percentiles.p50.toFixed(1)}</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-gray-600">75th</div>
          <div className="font-semibold">{percentiles.p75.toFixed(1)}</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="text-gray-600">90th</div>
          <div className="font-semibold">{percentiles.p90.toFixed(1)}</div>
        </div>
      </div>
    </div>
  );
}
