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
  const [year, setYear] = useState<YearType>(null);

  return (
    <YearContext.Provider value={{ year, setYear }}>
      {children}
    </YearContext.Provider>
  );
}

export function useYear() {
  return useContext(YearContext);
}