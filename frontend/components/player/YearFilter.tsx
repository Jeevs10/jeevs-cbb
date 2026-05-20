"use client";

import React, { useEffect } from "react";
import { YearType } from "@/types";

interface YearFilterProps {
  years: number[];
  selectedYear: YearType;
  onYearChange: (year: YearType) => void;
  loading?: boolean;
}

export const YearFilter = React.memo(function YearFilter({ years, selectedYear, onYearChange, loading }: YearFilterProps) {
  const handleYearChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    if (value === "all") {
      onYearChange(null);
    } else if (value === "career") {
      onYearChange("career");
    } else {
      onYearChange(parseInt(value));
    }
  };

  useEffect(() => {
    console.log("YearFilter years:", years);
  }, [years]);

  if (loading) {
    return (
      <div className="mb-3">
        <div className="animate-pulse">
          <div className="h-8 w-32 bg-gray-300 border border-gray-400"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3">
      <select
        value={selectedYear === null ? "all" : selectedYear === "career" ? "career" : String(selectedYear)}
        onChange={handleYearChange}
        className="px-2 py-1 border bg-white text-xs font-mono"
      >
        <option value="all">All Years</option>
        <option value="career">Career</option>
        {years.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
    </div>
  );
}, (prevProps, nextProps) => {
  // Only re-render if selectedYear changes
  return prevProps.selectedYear === nextProps.selectedYear &&
         prevProps.years.length === nextProps.years.length &&
         prevProps.loading === nextProps.loading;
});
