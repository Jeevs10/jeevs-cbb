"use client";

import React, { useMemo } from 'react';
import Panel, { PanelHeader } from "@/components/ui/Panel";

interface ClusterTransition {
  cluster_id: number;
  probability: number;
  name: string;
  avg_bpm: number;
  avg_usage: number;
  avg_height: number;
}

interface ClusterTransitionsData {
  current_cluster_id: number;
  stay_probability: number;
  destinations: ClusterTransition[];
}

interface ClusterTransitionMapProps {
  transitions: ClusterTransitionsData;
}

export default function ClusterTransitionMap({ transitions }: ClusterTransitionMapProps) {
  if (!transitions || transitions.destinations.length === 0) {
    return null;
  }

  const maxProbability = useMemo(() => Math.max(...transitions.destinations.map(d => d.probability)), [transitions.destinations.map(d => d.probability).join(',')]);

  return (
    <Panel>
      <PanelHeader>CLUSTER TRANSITION PROBABILITIES</PanelHeader>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">
          <span className="font-medium">Current Cluster:</span> {transitions.current_cluster_id}
        </div>
        <div className="text-sm text-gray-600">
          <span className="font-medium">Stay Probability:</span> {(transitions.stay_probability * 100).toFixed(1)}%
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="space-y-2">
        {transitions.destinations.map((dest) => (
          <div key={dest.cluster_id} className="border-b border-gray-100 pb-2">
            <div className="flex justify-between items-center mb-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">
                  {dest.cluster_id === transitions.current_cluster_id ? 'Stay' : `→ Cluster ${dest.cluster_id}`}
                </span>
                {dest.name && <span className="text-xs text-gray-500">({dest.name})</span>}
              </div>
              <span className="text-sm font-semibold text-purple-700">
                {(dest.probability * 100).toFixed(1)}%
              </span>
            </div>

            {/* Probability bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(dest.probability / maxProbability) * 100}%` }}
              />
            </div>

            {/* Cluster stats */}
            <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
              <div>
                <span className="text-gray-500">Avg BPM:</span> {dest.avg_bpm !== null && dest.avg_bpm !== undefined ? dest.avg_bpm.toFixed(1) : 'N/A'}
              </div>
              <div>
                <span className="text-gray-500">Usage:</span> {dest.avg_usage !== null && dest.avg_usage !== undefined ? dest.avg_usage.toFixed(1) : 'N/A'}%
              </div>
              <div>
                <span className="text-gray-500">Height:</span> {dest.avg_height !== null && dest.avg_height !== undefined ? dest.avg_height.toFixed(1) : 'N/A'}"
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
