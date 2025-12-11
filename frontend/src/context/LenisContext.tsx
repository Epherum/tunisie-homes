"use client";

import { createContext, useContext } from "react";

interface LenisContextType {
  start: () => void;
  stop: () => void;
}

const LenisContext = createContext<LenisContextType>({
  start: () => console.warn("LenisContext: start() called before provider"),
  stop: () => console.warn("LenisContext: stop() called before provider"),
});

export const useLenisControls = () => useContext(LenisContext);
export const LenisProvider = LenisContext.Provider;
