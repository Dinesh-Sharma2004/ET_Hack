import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [profile, setProfile] = useState(null);
  const [cache, setCache] = useState({});

  useEffect(() => {
    api
      .bootstrapSession()
      .then(() => api.getProfile())
      .then(setProfile)
      .catch(() => null);
  }, []);

  const value = useMemo(
    () => ({
      profile,
      setProfile,
      cache,
      setCached(key, value) {
        setCache((current) => ({ ...current, [key]: value }));
      }
    }),
    [cache, profile]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used inside AppProvider");
  }
  return context;
}
