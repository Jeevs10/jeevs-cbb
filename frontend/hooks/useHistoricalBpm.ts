import { useState, useEffect, useCallback } from "react";

interface HistoricalBpmData {
  year: number;
  BPM: number | null;
  Name: string;
  Team: string;
}

interface UseHistoricalBpmState {
  data: HistoricalBpmData[] | null;
  loading: boolean;
  error: string | null;
}

interface UseHistoricalBpmActions {
  refetch: () => void;
  clearError: () => void;
}

export function useHistoricalBpm(
  ncaaId: string
): UseHistoricalBpmState & UseHistoricalBpmActions {
  const [state, setState] = useState<UseHistoricalBpmState>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch(`/api/v1/players/${ncaaId}/historical-bpm`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch historical BPM");
      }

      const result = await response.json();
      setState({
        data: result.historical_bpm,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : "Failed to load historical BPM",
        data: null,
      }));
    }
  }, [ncaaId]);

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
