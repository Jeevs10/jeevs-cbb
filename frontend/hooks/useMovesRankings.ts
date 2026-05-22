import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";

interface MoveRanking {
  results: any[];
  count: number;
  filtered_count: number;
}

interface UseMovesRankingsParams {
  moveType: string;
  year?: number | string | null;
  limit?: number;
  offset?: number;
  position?: string;
  conference?: string;
  highMajor?: boolean;
  search?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export function useMovesRankings({ moveType, year, limit = 50, offset = 0, position, conference, highMajor, search, sortBy, sortOrder }: UseMovesRankingsParams) {
  const [data, setData] = useState<MoveRanking | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Clear data when moveType changes to ensure fresh data
  useEffect(() => {
    setData(null);
  }, [moveType]);

  useEffect(() => {
    const fetchRankings = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log("Fetching moves rankings with params:", { moveType, year, limit, offset, position, conference, highMajor, search, sortBy, sortOrder });

        const yearParam = year === "career" ? "career" : (typeof year === "number" ? year : (year ? parseInt(year) : undefined));

        const result = await apiClient.getMovesRankings(
          moveType,
          yearParam,
          limit,
          offset,
          position,
          conference,
          highMajor,
          search,
          sortBy,
          sortOrder
        );

        console.log("Moves rankings result:", result);

        if (result.error) {
          throw new Error(result.error);
        }

        setData(result);
      } catch (err) {
        console.error("Error fetching moves rankings:", err);
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, [moveType, year, limit, offset, position, conference, highMajor, search, sortBy, sortOrder]);

  return {
    data,
    loading,
    error,
    refetch: () => {
      // Trigger re-render by changing params
    },
  };
}
