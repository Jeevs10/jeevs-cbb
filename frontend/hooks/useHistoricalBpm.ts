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
      const response = await fetch(`/api/v1/players/${ncaaId}/history`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch player history");
      }

      const result = await response.json();

      const historicalBpm = result.history.map((h: any) => ({
        year: h.year,
        BPM: h.BPM,
        Name: h.player_name || h.Name,
        Team: h.team || h.Team
      }));

      setState({
        data: historicalBpm,
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
