"use client";

import React, { useRef } from "react";
import { YearType } from "@/types";

interface YearFilterProps {
  years: number[];
  selectedYear: YearType;
  onYearChange: (year: YearType) => void;
  loading?: boolean;
}

export const YearFilter = React.memo(function YearFilter({ years, selectedYear, onYearChange, loading }: YearFilterProps) {
  const isClickingRef = useRef(false);

  const handleYearClick = (event: React.MouseEvent, year: YearType) => {
    event.stopPropagation();
    if (isClickingRef.current) {
      return;
    }
    isClickingRef.current = true;
    onYearChange(year);
    setTimeout(() => {
      isClickingRef.current = false;
    }, 100);
  };

  if (loading) {
    return (
      <div className="mb-3 flex gap-2 flex-wrap">
        <div className="animate-pulse">
          <div className="h-8 w-16 bg-gray-300 border border-gray-400"></div>
        </div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-8 w-12 bg-gray-300 border border-gray-400"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="mb-3 flex gap-2 flex-wrap">
      <button
        onClick={(e) => handleYearClick(e, null)}
        className={`px-2 border transition-colors ${
          selectedYear === null 
            ? "font-bold underline bg-[#B7C4A5]" 
            : "hover:bg-[#e7e8d1]"
        }`}
      >
        ALL
      </button>

      {years.map((year) => (
        <button
          key={year}
          onClick={(e) => handleYearClick(e, year)}
          className={`px-2 border transition-colors ${
            selectedYear === year 
              ? "font-bold underline bg-[#B7C4A5]" 
              : "hover:bg-[#e7e8d1]"
          }`}
        >
          {year}
        </button>
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Only re-render if selectedYear changes
  return prevProps.selectedYear === nextProps.selectedYear &&
         prevProps.years.length === nextProps.years.length &&
         prevProps.loading === nextProps.loading;
});
