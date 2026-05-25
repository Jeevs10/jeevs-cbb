"use client";

import { useYear } from "@/app/context/YearContext";

interface YearToggleProps {
  availableYears?: number[];
  showCareer?: boolean;
}

export default function YearToggle({ availableYears = [], showCareer = true }: YearToggleProps) {
  const { year, setYear } = useYear();

  if (!availableYears || availableYears.length <= 1) return null;

  const handleYearChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    if (value === "career") {
      setYear("career");
    } else {
      setYear(parseInt(value));
    }
  };

  return (
    <div className="flex gap-2 mb-3 text-xs flex-wrap items-center">
      <select
        value={year === "career" ? "career" : String(year)}
        onChange={handleYearChange}
        className="px-2 py-1 border bg-white font-mono"
      >
        {showCareer && <option value="career">Career</option>}
        {availableYears.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </div>
  );
}