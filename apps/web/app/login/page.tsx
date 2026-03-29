'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiRequest } from '@/lib/api';
import { setAccessToken } from '@/lib/auth';
import type { TokenResponse } from '@/lib/types';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      const data = await apiRequest<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      setAccessToken(data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no login.');
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md items-center p-6">
      <form onSubmit={onSubmit} className="w-full space-y-4 rounded-2xl border bg-white p-6">
        <h1 className="text-2xl font-semibold">Entrar</h1>

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

        <button className="w-full rounded-xl bg-zinc-900 p-3 text-white">Entrar</button>
      </form>
    </div>
  );
}
