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
    } else {
      onYearChange(parseInt(value));
    }
  };


  if (loading) {
    return (
      <div className="mb-3">
        <div className="animate-pulse">
          <div className="h-8 w-32 bg-[#C7D0B8] border-2 border-black"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3">
      <select
        value={selectedYear === null ? "all" : String(selectedYear)}
        onChange={handleYearChange}
        className="px-2 py-1 border-2 border-black bg-[#C7D0B8] text-xs font-mono shadow-[3px_3px_0px_black]"
      >
        <option value="all">All Years</option>
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
