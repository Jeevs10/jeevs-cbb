"use client";

import { useYear } from "@/app/context/YearContext";

export default function YearToggle({ availableYears = [] }) {
  const { year, setYear } = useYear();

  if (!availableYears || availableYears.length <= 1) return null;

  return (
    <div className="flex gap-2 mb-3 text-xs flex-wrap">

      {/* Latest */}
      <button
        onClick={() => setYear(null)}
        className={`px-2 py-1 border ${
          year === null ? "bg-black text-white" : "bg-white"
        }`}
      >
        Latest
      </button>

      {/* Career */}
      <button
        onClick={() => setYear("career")}
        className={`px-2 py-1 border ${
          year === "career" ? "bg-black text-white" : "bg-white"
        }`}
      >
        Career
      </button>

      {/* Individual years */}
      {availableYears.map((y) => (
        <button
          key={y}
          onClick={() => setYear(y)}
          className={`px-2 py-1 border ${
            year === y ? "bg-black text-white" : "bg-white"
          }`}
        >
          {y}
        </button>
      ))}
    </div>
  );
}