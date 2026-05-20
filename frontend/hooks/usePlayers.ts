import { useState, useEffect, useCallback, useMemo } from "react";
import { apiClient } from "@/lib/api-client";
import { Player, PlayerStats, FetchPlayersParams } from "@/types";
import { handleApiError } from "@/lib/utils";

interface UsePlayersState {
  players: Player[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  filteredCount: number;
}

interface UsePlayersActions {
  refetch: () => void;
  clearError: () => void;
}

export function usePlayers(params: FetchPlayersParams = {}): UsePlayersState & UsePlayersActions {
  const [state, setState] = useState<UsePlayersState>({
    players: [],
    loading: true,
    error: null,
    totalCount: 0,
    filteredCount: 0,
  });

  // Memoize params to prevent infinite re-renders
  const memoizedParams = useMemo(() => params, [
    params.limit,
    params.offset,
    params.sort,
    params.order,
    params.year,
    params.search,
    params.d1Only,
    params.highMajorOnly,
    params.conf,
  ]);

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data: PlayerStats = await apiClient.getAllPlayers(memoizedParams);
      setState({
        players: data.results,
        loading: false,
        error: null,
        totalCount: data.count,
        filteredCount: data.filtered_count,
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: handleApiError(error),
        players: [],
        totalCount: 0,
        filteredCount: 0,
      }));
    }
  }, [memoizedParams]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    refetch: fetchData,
    clearError,
  };
}
