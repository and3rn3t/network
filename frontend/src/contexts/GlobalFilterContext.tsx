import type { TimeRange } from "@/components/TimeRangeSelector";
import React, { createContext, useContext, useMemo, useState } from "react";

interface GlobalFilterState {
  timeRange: TimeRange;
  siteId: string | null;
}

interface GlobalFilterContextValue extends GlobalFilterState {
  setTimeRange: (range: TimeRange) => void;
  setSiteId: (siteId: string | null) => void;
  resetFilters: () => void;
}

const DEFAULT_TIME_RANGE: TimeRange = {
  hours: 24,
  label: "Last 24 Hours",
};

const GlobalFilterContext = createContext<GlobalFilterContextValue | undefined>(
  undefined
);

export const GlobalFilterProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [timeRange, setTimeRangeState] =
    useState<TimeRange>(DEFAULT_TIME_RANGE);
  const [siteId, setSiteIdState] = useState<string | null>(null);

  const value = useMemo<GlobalFilterContextValue>(
    () => ({
      timeRange,
      siteId,
      setTimeRange: setTimeRangeState,
      setSiteId: setSiteIdState,
      resetFilters: () => {
        setTimeRangeState(DEFAULT_TIME_RANGE);
        setSiteIdState(null);
      },
    }),
    [timeRange, siteId]
  );

  return (
    <GlobalFilterContext.Provider value={value}>
      {children}
    </GlobalFilterContext.Provider>
  );
};

export const useGlobalFilters = (): GlobalFilterContextValue => {
  const context = useContext(GlobalFilterContext);

  if (!context) {
    throw new Error(
      "useGlobalFilters must be used within a GlobalFilterProvider"
    );
  }

  return context;
};
