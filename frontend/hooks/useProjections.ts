import { useState, useEffect, useCallback } from "react";

interface ProjectionYear {
  year: number;
  projected_bpm?: number;
  bpm_change?: number;
  confidence_interval?: [number, number];
  percentile_rank?: number;
  sample_size?: number;
  error?: string;
}

interface SimilarPlayer {
  player_key: string;
  player_name: string;
  year_from: number;
  year_to: number;
  bpm_change: number;
  similarity: number;
}

interface ClusterDescription {
  cluster_id: number;
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

interface ClusterTransition {
  cluster_id: number;
  probability: number;
  name: string;
  avg_bpm: number;
  avg_usage: number;
  avg_height: number;
}

interface ClusterTransitions {
  current_cluster_id: number;
  stay_probability: number;
  destinations: ClusterTransition[];
}

interface ProjectionData {
  success: boolean;
  player_id: string;
  current_year: number;
  cluster_id: number;
  cluster_description?: ClusterDescription;
  historical_samples: number;
  projections: ProjectionYear[];
  similar_players: SimilarPlayer[];
  cluster_transitions?: ClusterTransitions;
  methodology: string;
}

interface UseProjectionsState {
  data: ProjectionData | null;
  loading: boolean;
  error: string | null;
}

interface UseProjectionsActions {
  refetch: () => void;
  clearError: () => void;
}

export function useProjections(
  ncaaId: string,
  currentYear: number = 2026,
  yearsAhead: number = 1,
  minSamples: number = 10
): UseProjectionsState & UseProjectionsActions {
  const [state, setState] = useState<UseProjectionsState>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const params = new URLSearchParams({
        current_year: currentYear.toString(),
        years_ahead: yearsAhead.toString(),
        min_samples: minSamples.toString(),
      });

      const response = await fetch(
        `/api/v1/players/${ncaaId}/projections?${params.toString()}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch projections");
      }

      const data: ProjectionData = await response.json();
      setState({
        data,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : "Failed to load projections",
        data: null,
      }));
    }
  }, [ncaaId, currentYear, yearsAhead, minSamples]);

  useEffect(() => {
    if (ncaaId) {
      fetchData();
    }
  }, [fetchData, ncaaId]);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    refetch: fetchData,
    clearError,
  };
}
