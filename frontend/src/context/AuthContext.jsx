import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setUnauthorizedHandler, tokenStore } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(tokenStore.get()));

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  // an expired token anywhere in the app just drops you back to the login screen
  useEffect(() => setUnauthorizedHandler(logout), [logout]);

  useEffect(() => {
    if (!tokenStore.get()) return;
    api
      .me()
      .then(setUser)
      .catch(logout)
      .finally(() => setChecking(false));
  }, [logout]);

  const startSession = useCallback(({ access_token, user: signedIn }) => {
    tokenStore.set(access_token);
    setUser(signedIn);
  }, []);

  const value = useMemo(
    () => ({
      user,
      checking,
      logout,
      login: async (form) => startSession(await api.login(form)),
      register: async (form) => startSession(await api.register(form)),
    }),
    [user, checking, logout, startSession],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
