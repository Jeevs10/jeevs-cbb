"use client";

import React, { useMemo } from 'react';
import Panel, { PanelHeader } from "@/components/ui/Panel";

interface ClusterDescription {
  cluster_id: number;
  avg_bpm: number;
  avg_usage: number;
  avg_height: number;
  avg_rim_freq: number;
  avg_3pt_pct: number;
}

interface Projection {
  year: number;
  projected_bpm: number;
  bpm_change: number;
}

interface PlayerClusterDistributionProps {
  currentBpm: number;
  clusterDescription: ClusterDescription;
  projections: Projection[];
  distribution?: number[]; // Actual BPM values from cluster
}

export default function PlayerClusterDistribution({
  currentBpm,
  clusterDescription,
  projections,
  distribution = []
}: PlayerClusterDistributionProps) {
  if (!clusterDescription || !projections || projections.length === 0) {
    return null;
  }

  const projection = projections[0];
  const projectedBpm = projection.projected_bpm;

  // Create smooth distribution curve from distribution data
  const distributionCurve = useMemo(() => {
    if (distribution.length === 0) {
      // Fallback to normal distribution if no data
      const stdDev = 2.0;
      const points = [];
      const range = 3 * stdDev;
      const step = range / 100;
      for (let i = 0; i <= 100; i++) {
        const x = clusterDescription.avg_bpm - range + (i * step);
        const y = Math.exp(-0.5 * Math.pow((x - clusterDescription.avg_bpm) / stdDev, 2));
        points.push({ x, y });
      }
      return points;
    }

    // Use Gaussian kernel density estimation directly on raw data
    const minBpm = Math.min(...distribution);
    const maxBpm = Math.max(...distribution);
    const smoothPoints = [];
    const numPoints = 200;
    const bandwidth = (maxBpm - minBpm) / 8; // Bandwidth for smoothing

    for (let i = 0; i <= numPoints; i++) {
      const x = minBpm + (i * (maxBpm - minBpm) / numPoints);

      // Gaussian kernel density estimation
      let y = 0;

      for (const bpm of distribution) {
        const diff = x - bpm;
        const weight = Math.exp(-(diff * diff) / (2 * bandwidth * bandwidth));
        y += weight;
      }

      y = y / (distribution.length * bandwidth * Math.sqrt(2 * Math.PI));
      smoothPoints.push({ x, y });
    }

    // Normalize y values to 0-1 range
    const maxYVal = Math.max(...smoothPoints.map(p => p.y));
    if (maxYVal > 0) {
      smoothPoints.forEach(p => p.y = p.y / maxYVal);
    }

    return smoothPoints;
  }, [distribution, clusterDescription.avg_bpm]);

  // Find x-axis range for visualization - center around peak
  const allX = useMemo(() => distributionCurve.map(p => p.x), [distributionCurve]);
  const dataMinX = useMemo(() => Math.min(...allX), [allX]);
  const dataMaxX = useMemo(() => Math.max(...allX), [allX]);

  // Find the peak of the distribution
  const peakPoint = useMemo(() => {
    const peakIndex = distributionCurve.findIndex(p => p.y === Math.max(...distributionCurve.map(p => p.y)));
    return distributionCurve[peakIndex] || { x: clusterDescription.avg_bpm };
  }, [distributionCurve, clusterDescription.avg_bpm]);

  // Calculate range needed to include current and projected BPM
  const maxDistanceFromPeak = useMemo(() => {
    const currentDist = Math.abs(currentBpm - peakPoint.x);
    const projectedDist = Math.abs(projectedBpm - peakPoint.x);
    const dataDist = Math.max(Math.abs(dataMinX - peakPoint.x), Math.abs(dataMaxX - peakPoint.x));
    return Math.max(currentDist, projectedDist, dataDist);
  }, [currentBpm, projectedBpm, dataMinX, dataMaxX, peakPoint.x]);

  // Add some padding (20% on each side)
  const paddingFactor = 1.2;
  const range = maxDistanceFromPeak * paddingFactor;
  const minX = useMemo(() => peakPoint.x - range, [peakPoint.x, range]);
  const maxX = useMemo(() => peakPoint.x + range, [peakPoint.x, range]);
  const xRange = useMemo(() => maxX - minX, [maxX, minX]);
  const maxY = useMemo(() => Math.max(...distributionCurve.map(p => p.y)), [distributionCurve]);

  const svgHeight = 200;
  const svgWidth = 400;
  const padding = { top: 20, right: 20, bottom: 60, left: 20 };
  const plotWidth = svgWidth - padding.left - padding.right;
  const plotHeight = svgHeight - padding.top - padding.bottom;

  // Create smooth curve path
  const curvePath = useMemo(() => {
    if (distributionCurve.length === 0) return '';

    const points = distributionCurve.map((point, index) => {
      const x = padding.left + ((point.x - minX) / xRange) * plotWidth;
      const y = padding.top + plotHeight - ((point.y / maxY) * plotHeight);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    });

    return points.join(' ');
  }, [distributionCurve, minX, xRange, maxY, plotWidth, plotHeight, padding]);

  // Create area under curve
  const areaPath = useMemo(() => {
    if (distributionCurve.length === 0) return '';

    const points = distributionCurve.map((point, index) => {
      const x = padding.left + ((point.x - minX) / xRange) * plotWidth;
      const y = padding.top + plotHeight - ((point.y / maxY) * plotHeight);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    });

    const firstX = padding.left + ((distributionCurve[0].x - minX) / xRange) * plotWidth;
    const lastX = padding.left + ((distributionCurve[distributionCurve.length - 1].x - minX) / xRange) * plotWidth;
    const bottomY = padding.top + plotHeight;

    return `${points.join(' ')} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;
  }, [distributionCurve, minX, xRange, maxY, plotWidth, plotHeight, padding]);

  // Calculate percentile of current player within cluster
  const calculatePercentile = useMemo(() => (value: number) => {
    if (distribution.length === 0) {
      // Fallback to normal distribution
      const stdDev = 2.0;
      const z = (value - clusterDescription.avg_bpm) / stdDev;
      return 0.5 * (1 + Math.sign(z) * (1 - Math.exp(-2 * z * z / Math.PI)));
    }
    // Actual percentile from distribution
    const count = distribution.filter(bpm => bpm <= value).length;
    return count / distribution.length;
  }, [distribution, clusterDescription.avg_bpm]);

  const currentPercentile = useMemo(() => calculatePercentile(currentBpm), [calculatePercentile, currentBpm]);
  const projectedPercentile = useMemo(() => calculatePercentile(projectedBpm), [calculatePercentile, projectedBpm]);

  return (
    <Panel>
      <PanelHeader>PLAYER POSITION VS CLUSTER DISTRIBUTION</PanelHeader>

      {/* Distribution Histogram */}
      <div className="mb-4">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-64">
          {/* Grid lines */}
          <line x1={padding.left} y1={padding.top + plotHeight * 0.5} x2={padding.left + plotWidth} y2={padding.top + plotHeight * 0.5} stroke="#000" strokeWidth="0.5" />
          <line x1={padding.left} y1={padding.top + plotHeight * 0.25} x2={padding.left + plotWidth} y2={padding.top + plotHeight * 0.25} stroke="#000" strokeWidth="0.5" />
          <line x1={padding.left} y1={padding.top + plotHeight * 0.75} x2={padding.left + plotWidth} y2={padding.top + plotHeight * 0.75} stroke="#000" strokeWidth="0.5" />

          {/* Area under curve */}
          <path
            d={areaPath}
            fill="rgba(0, 0, 0, 0.1)"
            stroke="none"
          />
          {/* Smooth curve */}
          <path
            d={curvePath}
            fill="none"
            stroke="#000"
            strokeWidth="2"
          />

          {/* Current BPM marker - vertical dashed line */}
          <line
            x1={padding.left + ((currentBpm - minX) / xRange) * plotWidth}
            y1={padding.top}
            x2={padding.left + ((currentBpm - minX) / xRange) * plotWidth}
            y2={padding.top + plotHeight}
            stroke="#000"
            strokeWidth="2"
            strokeDasharray="6,4"
          />
          <circle
            cx={padding.left + ((currentBpm - minX) / xRange) * plotWidth}
            cy={padding.top + plotHeight - 5}
            r="5"
            fill="#000"
            stroke="white"
            strokeWidth="2"
          />

          {/* Projected BPM marker - vertical dashed line */}
          <line
            x1={padding.left + ((projectedBpm - minX) / xRange) * plotWidth}
            y1={padding.top}
            x2={padding.left + ((projectedBpm - minX) / xRange) * plotWidth}
            y2={padding.top + plotHeight}
            stroke="#000"
            strokeWidth="2"
            strokeDasharray="2,2"
          />
          <circle
            cx={padding.left + ((projectedBpm - minX) / xRange) * plotWidth}
            cy={padding.top + plotHeight - 5}
            r="5"
            fill="white"
            stroke="#000"
            strokeWidth="2"
          />

          {/* X-axis labels - use more granular scale */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const x = padding.left + (pct * plotWidth);
            const value = minX + (pct * xRange);
            return (
              <text key={pct} x={x} y={svgHeight - 35} fontSize="12" fill="#000" textAnchor="middle">
                {value.toFixed(1)}
              </text>
            );
          })}
          {/* X-axis label */}
          <text x={padding.left + plotWidth / 2} y={svgHeight - 50} fontSize="11" fill="#000" textAnchor="middle">
            BPM
          </text>
        </svg>

        {/* Legend */}
        <div className="mt-3 flex justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 bg-black" />
            <span className="font-bold text-black uppercase tracking-wide">Current: {currentBpm.toFixed(1)} BPM</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 bg-white border-2 border-black" />
            <span className="font-bold text-black uppercase tracking-wide">Projected: {projectedBpm.toFixed(1)} BPM</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="border-2 border-black bg-[#C7D0B8] p-3">
          <div className="mb-1 font-bold text-black uppercase tracking-wide">CURRENT POSITION</div>
          <div className="text-sm font-bold text-black">{(currentPercentile * 100).toFixed(0)}th percentile</div>
          <div className="text-black">
            {currentBpm.toFixed(1)} BPM in cluster
          </div>
        </div>
        <div className="border-2 border-black bg-[#C7D0B8] p-3">
          <div className="mb-1 font-bold text-black uppercase tracking-wide">PROJECTED POSITION</div>
          <div className="text-sm font-bold text-black">{(projectedPercentile * 100).toFixed(0)}th percentile</div>
          <div className="text-black">
            {projectedBpm.toFixed(1)} BPM in cluster
          </div>
        </div>
      </div>

      {/* Cluster Context */}
      <div className="mt-3 border-2 border-black bg-[#E7E8D1] p-3 text-xs">
        <div className="mb-2 font-bold text-black uppercase tracking-wide">CLUSTER CONTEXT (CLUSTER {clusterDescription.cluster_id})</div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <span className="text-black">Avg BPM:</span>{' '}
            <span className="font-bold text-black">
              {clusterDescription.avg_bpm !== null && clusterDescription.avg_bpm !== undefined ? clusterDescription.avg_bpm.toFixed(1) : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-black">Avg Usage:</span>{' '}
            <span className="font-bold text-black">
              {clusterDescription.avg_usage !== null && clusterDescription.avg_usage !== undefined ? clusterDescription.avg_usage.toFixed(1) : 'N/A'}%
            </span>
          </div>
          <div>
            <span className="text-black">Avg Height:</span>{' '}
            <span className="font-bold text-black">
              {clusterDescription.avg_height !== null && clusterDescription.avg_height !== undefined ? clusterDescription.avg_height.toFixed(1) : 'N/A'}"
            </span>
          </div>
        </div>
      </div>
    </Panel>
  );
}
