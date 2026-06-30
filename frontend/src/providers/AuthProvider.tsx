"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { AuthService } from "@/services/auth.service";
import type { User } from "@/types/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const AuthContext =
  createContext<AuthContextType | null>(
    null
  );

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(true);

  async function refreshUser() {
    try {
      setLoading(true);

      const currentUser =
        await AuthService.getCurrentUser();

      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    AuthService.logout();

    setUser(null);

    window.location.href = "/login";
  }

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used within AuthProvider"
    );
  }

  return context;
}