"use client";

import { useState } from "react";

interface ProjectionYear {
  year: number;
  projected_bpm?: number;
  bpm_change?: number;
  confidence_interval?: [number, number];
  percentile_rank?: number;
  sample_size?: number;
  error?: string;
}

interface ClusterDescription {
  cluster_id: number;
  name?: string;
  count: number;
  avg_height: number;
  avg_usage: number;
  avg_rim_freq: number;
  avg_3pt_pct: number;
  avg_bpm: number;
  top_players: Array<{
    Name: string;
    Team: string;
    BPM: number;
  }>;
}

interface SimilarPlayer {
  player_key: string;
  player_name: string;
  year_from?: number;
  year_to?: number;
  bpm_change?: number;
  similarity: number;
  career_bpm?: Array<{
    year: number;
    bpm: number;
  }>;
}

interface PlayerProjectionTableProps {
  currentBpm: number;
  currentYear: number;
  projections: ProjectionYear[];
  clusterDescription?: ClusterDescription;
  similarPlayers: SimilarPlayer[];
  historicalSamples: number;
  playerName?: string;
}

export default function PlayerProjectionTable({
  currentBpm,
  currentYear,
  projections,
  clusterDescription,
  similarPlayers,
  historicalSamples,
  playerName,
}: PlayerProjectionTableProps) {
  const [showGraph, setShowGraph] = useState(false);

  const getChangeColor = (change: number) => {
    if (change > 0) return "text-black";
    if (change < 0) return "text-black";
    return "text-black";
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return "↑";
    if (change < 0) return "↓";
    return "→";
  };

  return (
    <div className="space-y-6">
      {/* Cluster Information */}
      {clusterDescription && (
        <div className="border-2 border-black bg-[#C7D0B8] p-3">
          <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
            Cluster Analysis
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <div>
              <span className="text-black">Cluster ID:</span>
              <span className="ml-2 font-bold">{clusterDescription.cluster_id}</span>
            </div>
            <div>
              <span className="text-black">Players in Cluster:</span>
              <span className="ml-2 font-bold">{clusterDescription.count}</span>
            </div>
            <div>
              <span className="text-black">Avg BPM:</span>
              <span className="ml-2 font-bold">
                {clusterDescription.avg_bpm !== null && clusterDescription.avg_bpm !== undefined
                  ? clusterDescription.avg_bpm.toFixed(2)
                  : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-black">Historical Samples:</span>
              <span className="ml-2 font-bold">{historicalSamples}</span>
            </div>
          </div>
        </div>
      )}

      {/* Projection Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border-2 border-black">
          <thead>
            <tr className="border-b-2 border-black bg-[#B8C0A8]">
              <th className="text-left py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">Year</th>
              <th className="text-left py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">Status</th>
              <th className="text-right py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">BPM</th>
              <th className="text-right py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">Change</th>
              <th className="text-right py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">95% CI</th>
              <th className="text-right py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">Growth Percentile</th>
              <th className="text-right py-2 px-3 font-bold text-black text-xs uppercase tracking-wide">Sample Size</th>
            </tr>
          </thead>
          <tbody>
            {/* Current Year */}
            <tr className="border-b-2 border-black bg-[#E7E8D1]">
              <td className="py-2 px-3 font-bold text-black text-xs">{currentYear}</td>
              <td className="py-2 px-3">
                <span className="inline-flex items-center px-2 py-1 border-2 border-black bg-[#C7D0B8] text-black text-xs font-bold uppercase tracking-wide">
                  Actual
                </span>
              </td>
              <td className="py-2 px-3 text-right font-bold text-black text-xs">{currentBpm.toFixed(2)}</td>
              <td className="py-2 px-3 text-right text-black text-xs">—</td>
              <td className="py-2 px-3 text-right text-black text-xs">—</td>
              <td className="py-2 px-3 text-right text-black text-xs">—</td>
              <td className="py-2 px-3 text-right text-black text-xs">—</td>
            </tr>

            {/* Projection Years */}
            {projections.map((projection) => (
              <tr key={projection.year} className="border-b-2 border-black hover:bg-[#B8C0A8]">
                <td className="py-2 px-3 font-bold text-black text-xs">{projection.year}</td>
                <td className="py-2 px-3">
                  {projection.error ? (
                    <span className="inline-flex items-center px-2 py-1 border-2 border-black bg-[#E7E8D1] text-black text-xs font-bold uppercase tracking-wide">
                      Error
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 border-2 border-black bg-[#C7D0B8] text-black text-xs font-bold uppercase tracking-wide">
                      Projected
                    </span>
                  )}
                </td>
                <td className="py-2 px-3 text-right font-bold text-black text-xs">
                  {projection.projected_bpm !== undefined ? (
                    projection.projected_bpm.toFixed(2)
                  ) : (
                    <span className="text-black text-xs">—</span>
                  )}
                </td>
                <td className={`py-2 px-3 text-right font-bold text-black text-xs ${getChangeColor(projection.bpm_change || 0)}`}>
                  {projection.bpm_change !== undefined ? (
                    <span>
                      {getChangeIcon(projection.bpm_change)} {Math.abs(projection.bpm_change).toFixed(2)}
                    </span>
                  ) : (
                    <span className="text-black text-xs">—</span>
                  )}
                </td>
                <td className="py-2 px-3 text-right text-xs text-black">
                  {projection.confidence_interval ? (
                    `${projection.confidence_interval[0].toFixed(1)} - ${projection.confidence_interval[1].toFixed(1)}`
                  ) : (
                    <span className="text-black text-xs">—</span>
                  )}
                </td>
                <td className="py-2 px-3 text-right text-xs text-black">
                  {projection.percentile_rank !== undefined ? (
                    <span className="font-bold text-black text-xs">
                      {(projection.percentile_rank * 100).toFixed(0)}%
                    </span>
                  ) : (
                    <span className="text-black text-xs">—</span>
                  )}
                </td>
                <td className="py-2 px-3 text-right text-xs text-black">
                  {projection.sample_size !== undefined ? projection.sample_size : <span className="text-black text-xs">—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Similar Players */}
      {similarPlayers.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold text-black uppercase tracking-wide">
              Most Similar Historical Players
            </h3>
            <button
              onClick={() => setShowGraph(!showGraph)}
              className="text-xs px-3 py-1 border-2 border-black bg-[#C7D0B8] text-black font-bold uppercase tracking-wide hover:bg-[#B8C0A8]"
            >
              {showGraph ? "Show Table" : "Show Graph"}
            </button>
          </div>

          {showGraph ? (
            <div className="border-2 border-black bg-[#C7D0B8] p-3">
              <div className="h-72 relative mb-4">
                <svg viewBox="0 0 550 280" className="w-full h-full">
                  {(() => {
                    const groupedPlayers = similarPlayers.reduce((acc, player) => {
                      if (!acc[player.player_key]) {
                        acc[player.player_key] = {
                          player_key: player.player_key,
                          player_name: player.player_name,
                          similarity: player.similarity,
                          career_bpm: player.career_bpm || []
                        };
                      }
                      return acc;
                    }, {} as Record<string, any>);

                    const sortedPlayers = Object.values(groupedPlayers)
                      .sort((a: any, b: any) => b.similarity - a.similarity)
                      .slice(0, 5);

                    // Get all BPM values across all players for scaling
                    const allBpms = sortedPlayers.flatMap((p: any) => p.career_bpm.map((d: any) => d.bpm));

                    // Add current player's BPM and projection
                    allBpms.push(currentBpm);
                    if (projections.length > 0 && projections[0].projected_bpm) {
                      allBpms.push(projections[0].projected_bpm);
                    }

                    const minBpm = Math.min(...allBpms, 0);
                    const maxBpm = Math.max(...allBpms, 15);
                    const range = maxBpm - minBpm || 1;
                    const width = 550;
                    const height = 280;
                    const padding = 60;

                    // Get all unique years for x-axis
                    const allYears = Array.from(new Set(
                      sortedPlayers.flatMap((p: any) => p.career_bpm.map((d: any) => d.year))
                    )).sort((a, b) => a - b);

                    // Add current year and projected year
                    allYears.push(currentYear);
                    if (projections.length > 0) {
                      allYears.push(projections[0].year);
                    }
                    allYears.sort((a, b) => a - b);

                    const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

                    // Build selected player trajectory
                    const selectedPlayerTrajectory = [
                      { year: currentYear, bpm: currentBpm }
                    ];
                    if (projections.length > 0 && projections[0].projected_bpm) {
                      selectedPlayerTrajectory.push({
                        year: projections[0].year,
                        bpm: projections[0].projected_bpm
                      });
                    }

                    return (
                      <>
                        {/* Background */}
                        <rect x={padding} y={padding} width={width - 2 * padding} height={height - 2 * padding} fill="#f9fafb" rx="4" />

                        {/* Grid lines */}
                        {[0, 0.25, 0.5, 0.75, 1].map((frac) => (
                          <line
                            key={frac}
                            x1={padding}
                            y1={height - padding - frac * (height - 2 * padding)}
                            x2={width - padding}
                            y2={height - padding - frac * (height - 2 * padding)}
                            stroke="#e5e7eb"
                            strokeWidth="1"
                            strokeDasharray="4,4"
                          />
                        ))}
                        {/* Y-axis labels */}
                        {[0, 0.25, 0.5, 0.75, 1].map((frac) => {
                          const bpmValue = minBpm + frac * range;
                          return (
                            <text
                              key={frac}
                              x={padding - 15}
                              y={height - padding - frac * (height - 2 * padding) + 4}
                              textAnchor="end"
                              fontSize="11"
                              fill="#6b7280"
                              fontFamily="system-ui, -apple-system, sans-serif"
                            >
                              {bpmValue.toFixed(1)}
                            </text>
                          );
                        })}
                        {/* Year labels */}
                        {allYears.map((year) => {
                          const x = padding + ((year - allYears[0]) / (allYears[allYears.length - 1] - allYears[0] || 1)) * (width - 2 * padding);
                          return (
                            <text
                              key={year}
                              x={x}
                              y={height - padding + 20}
                              textAnchor="middle"
                              fontSize="11"
                              fill="#6b7280"
                              fontFamily="system-ui, -apple-system, sans-serif"
                            >
                              {year}
                            </text>
                          );
                        })}
                        {/* Selected player line (thicker, black) */}
                        {selectedPlayerTrajectory.length > 1 && (
                          <g>
                            <polyline
                              points={selectedPlayerTrajectory.map((d: any) => {
                                const x = padding + ((d.year - allYears[0]) / (allYears[allYears.length - 1] - allYears[0] || 1)) * (width - 2 * padding);
                                const y = height - padding - ((d.bpm - minBpm) / range) * (height - 2 * padding);
                                return `${x},${y}`;
                              }).join(' ')}
                              fill="none"
                              stroke="#1f2937"
                              strokeWidth="3"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                            {selectedPlayerTrajectory.map((d: any, i: number) => {
                              const x = padding + ((d.year - allYears[0]) / (allYears[allYears.length - 1] - allYears[0] || 1)) * (width - 2 * padding);
                              const y = height - padding - ((d.bpm - minBpm) / range) * (height - 2 * padding);
                              return (
                                <circle
                                  key={i}
                                  cx={x}
                                  cy={y}
                                  r="5"
                                  fill="#1f2937"
                                  stroke="#fff"
                                  strokeWidth="2"
                                />
                              );
                            })}
                          </g>
                        )}
                        {/* Lines for each similar player */}
                        {sortedPlayers.map((player: any, playerIdx: number) => {
                          if (!player.career_bpm || player.career_bpm.length === 0) return null;

                          const color = colors[playerIdx % colors.length];
                          const points = player.career_bpm.map((d: any) => {
                            const x = padding + ((d.year - allYears[0]) / (allYears[allYears.length - 1] - allYears[0] || 1)) * (width - 2 * padding);
                            const y = height - padding - ((d.bpm - minBpm) / range) * (height - 2 * padding);
                            return `${x},${y}`;
                          }).join(' ');

                          return (
                            <g key={player.player_key}>
                              <polyline
                                points={points}
                                fill="none"
                                stroke={color}
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                opacity="0.6"
                              />
                              {player.career_bpm.map((d: any, i: number) => {
                                const x = padding + ((d.year - allYears[0]) / (allYears[allYears.length - 1] - allYears[0] || 1)) * (width - 2 * padding);
                                const y = height - padding - ((d.bpm - minBpm) / range) * (height - 2 * padding);
                                return (
                                  <circle
                                    key={i}
                                    cx={x}
                                    cy={y}
                                    r="3"
                                    fill={color}
                                    stroke="#fff"
                                    strokeWidth="1"
                                  />
                                );
                              })}
                            </g>
                          );
                        })}
                      </>
                    );
                  })()}
                </svg>
              </div>
              {/* Legend below graph */}
              <div className="flex flex-wrap gap-4 justify-center text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-gray-800"></div>
                  <span className="font-medium text-gray-900">{playerName || 'Selected Player'}</span>
                </div>
                {(() => {
                  const groupedPlayers = similarPlayers.reduce((acc, player) => {
                    if (!acc[player.player_key]) {
                      acc[player.player_key] = {
                        player_key: player.player_key,
                        player_name: player.player_name,
                        similarity: player.similarity,
                        career_bpm: player.career_bpm || []
                      };
                    }
                    return acc;
                  }, {} as Record<string, any>);

                  const sortedPlayers = Object.values(groupedPlayers)
                    .sort((a: any, b: any) => b.similarity - a.similarity)
                    .slice(0, 5);

                  const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

                  return sortedPlayers.map((player: any, idx: number) => (
                    <div key={player.player_key} className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: colors[idx % colors.length] }}></div>
                      <span className="text-gray-700">{player.player_name}</span>
                    </div>
                  ));
                })()}
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left py-2 px-4 font-semibold text-gray-700 text-sm">Player</th>
                    <th className="text-left py-2 px-4 font-semibold text-gray-700 text-sm">Career Trajectory</th>
                    <th className="text-right py-2 px-4 font-semibold text-gray-700 text-sm">Similarity</th>
                  </tr>
                </thead>
                <tbody>
                  {(() => {
                    const groupedPlayers = similarPlayers.reduce((acc, player) => {
                      if (!acc[player.player_key]) {
                        acc[player.player_key] = {
                          player_key: player.player_key,
                          player_name: player.player_name,
                          similarity: player.similarity,
                          career_bpm: player.career_bpm || []
                        };
                      }
                      return acc;
                    }, {} as Record<string, any>);

                    const sortedPlayers = Object.values(groupedPlayers)
                      .sort((a: any, b: any) => b.similarity - a.similarity)
                      .slice(0, 5);

                    return sortedPlayers.map((player: any) => (
                      <tr key={player.player_key} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm font-medium">{player.player_name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {player.career_bpm && player.career_bpm.length > 0 ? (
                            <div className="flex items-center space-x-2">
                              {player.career_bpm.map((data: any) => (
                                <div key={data.year} className="flex flex-col items-center">
                                  <span className="text-xs font-medium">{data.bpm.toFixed(1)}</span>
                                  <span className="text-xs text-gray-500">{data.year}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <span className="text-gray-400">No career data</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right text-sm">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {(player.similarity * 100).toFixed(0)}%
                          </span>
                        </td>
                      </tr>
                    ));
                  })()}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Methodology Note */}
      <div className="text-xs text-black mt-4 p-3 border-2 border-black bg-[#E7E8D1]">
        <span className="font-bold uppercase tracking-wide">Methodology:</span> Projections are based on historical year-over-year BPM changes from players in the same cluster, weighted by feature similarity (Usage, BPM, Height, offensive/defensive ratings). Confidence intervals represent 95% statistical confidence bounds.
      </div>
    </div>
  );
}
