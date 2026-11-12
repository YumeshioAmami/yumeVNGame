import { createContext, useContext } from "react";
import type { Bootstrap } from "./types";

export interface AppContextValue {
  data: Bootstrap;
  refresh: () => Promise<void>;
  theme: string;
  setTheme: (theme: string) => void;
}

export const AppContext = createContext<AppContextValue | null>(null);

export function useApp(): AppContextValue {
  const value = useContext(AppContext);
  if (!value) throw new Error("AppContext is not ready");
  return value;
}

