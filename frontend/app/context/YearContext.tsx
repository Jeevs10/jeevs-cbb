"use client";

import { createContext, useContext, useState } from "react";

type YearType = number | null | "career";

const YearContext = createContext<{
  year: YearType;
  setYear: (y: YearType) => void;
}>({
  year: null,
  setYear: () => {},
});

export function YearProvider({ children }: { children: React.ReactNode }) {
  const [year, setYear] = useState<YearType>(2026); // Default to 2026 for BPM support

  return (
    <YearContext.Provider value={{ year, setYear }}>
      {children}
    </YearContext.Provider>
  );
}

export function useYear() {
  return useContext(YearContext);
}