import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import { handleApiError } from "@/lib/utils";

interface UseYearsState {
  years: number[];
  loading: boolean;
  error: string | null;
}

interface UseYearsActions {
  refetch: () => void;
  clearError: () => void;
}

export function useYears(): UseYearsState & UseYearsActions {
  const [state, setState] = useState<UseYearsState>({
    years: [],
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const years = await apiClient.getYears();
      setState({
        years,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: handleApiError(error),
        years: [],
      }));
    }
  }, []);

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
