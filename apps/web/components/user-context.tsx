'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

import { apiRequest } from '@/lib/api';
import { getAccessToken, clearAccessToken } from '@/lib/auth';
import type { User } from '@/lib/types';

interface UserContextType {
  user: User | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const userData = await apiRequest<User>('/auth/me', { method: 'GET' }, token);
      setUser(userData);
    } catch (error) {
      console.error('Erro ao obter usuário:', error);
      clearAccessToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    clearAccessToken();
    setUser(null);
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, refreshUser, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
