'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiRequest } from '@/lib/api';
import { setAccessToken } from '@/lib/auth';
import type { TokenResponse } from '@/lib/types';

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar se já existe usuário no sistema
    const checkSetup = async () => {
      try {
        const response = await apiRequest<{has_users: boolean, user_count: number}>('/auth/check-setup', { method: 'GET' });
        if (response.has_users) {
          // Se já tem usuários, redirecionar para login
          router.push('/login');
          return;
        }
      } catch (err) {
        // Se der erro, permite o registro (fallback)
        console.error('Erro ao verificar setup:', err);
      } finally {
        setIsLoading(false);
      }
    };

    checkSetup();
  }, [router]);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      const data = await apiRequest<TokenResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ full_name: fullName, email, password }),
      });

      setAccessToken(data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no cadastro.');
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md items-center p-6">
        <div className="w-full text-center">
          <p>Verificando configuração do sistema...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md items-center p-6">
      <form onSubmit={onSubmit} className="w-full space-y-4 rounded-2xl border bg-white p-6">
        <div>
          <h1 className="text-2xl font-semibold">Criar conta</h1>
          <p className="text-sm text-zinc-600 mt-1">
            O primeiro usuário será automaticamente administrador do sistema
          </p>
        </div>

        <input
          className="w-full rounded-xl border p-3"
          placeholder="Nome completo"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />

        <input
          className="w-full rounded-xl border p-3"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full rounded-xl border p-3"
          placeholder="Senha"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error ? (
          <div className="rounded-xl border border-red-300 bg-red-50 p-3 text-red-700">
            {error}
          </div>
        ) : null}

        <button className="w-full rounded-xl bg-zinc-900 p-3 text-white">Criar conta</button>
      </form>
    </div>
  );
}
