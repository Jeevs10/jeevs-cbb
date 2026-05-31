import { useState, useEffect, useCallback } from "react";

interface ClusterBpmDistribution {
  cluster_id: number;
  avg_bpm: number;
  count: number;
  distribution: number[];
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p10: number;
  };
  sample_size: number;
}

interface UseClusterBpmDistributionState {
  data: ClusterBpmDistribution | null;
  loading: boolean;
  error: string | null;
}

interface UseClusterBpmDistributionActions {
  refetch: () => void;
  clearError: () => void;
}

export function useClusterBpmDistribution(
  clusterId: number
): UseClusterBpmDistributionState & UseClusterBpmDistributionActions {
  const [state, setState] = useState<UseClusterBpmDistributionState>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch(`/api/v1/clusters/${clusterId}/bpm-distribution`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch cluster BPM distribution");
      }

      const data: ClusterBpmDistribution = await response.json();
      setState({
        data,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : "Failed to load cluster BPM distribution",
        data: null,
      }));
    }
  }, [clusterId]);

  useEffect(() => {
    if (clusterId) {
      fetchData();
    }
  }, [fetchData, clusterId]);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    refetch: fetchData,
    clearError,
  };
}
