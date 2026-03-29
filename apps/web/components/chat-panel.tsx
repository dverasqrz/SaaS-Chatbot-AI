'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createPortal } from 'react-dom';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport, type UIMessage } from 'ai';

import { apiRequest } from '@/lib/api';
import { friendlyChatErrorMessage } from '@/lib/chat-errors';
import { formatDateTimeRecife, formatShortRecife } from '@/lib/format-time';
import { getAccessToken, clearAccessToken } from '@/lib/auth';
import { useUser } from '@/components/user-context';
import {
  GROQ_DEFAULT_MODEL_ID,
  GROQ_MODEL_OPTIONS,
} from '@/lib/groq-models';
import type { Conversation, Message, Workspace } from '@/lib/types';

type ProviderName = 'groq' | 'openai' | 'google';

type MessageMeta = { createdAt?: string };

function messagesToUiMessages(rows: Message[]): UIMessage[] {
  return rows.map((item) => ({
    id: item.id,
    role: item.role as 'user' | 'assistant',
    metadata: { createdAt: item.created_at } satisfies MessageMeta,
    parts: [{ type: 'text' as const, text: item.content }],
  }));
}

function extractAllTextParts(message: UIMessage): string {
  if (!message.parts?.length) {
    return '';
  }
  return message.parts
    .map((part) => {
      if (part.type === 'text' && 'text' in part) {
        return String((part as { text?: string }).text ?? '');
      }
      if (part.type === 'reasoning' && 'text' in part) {
        return String((part as { text?: string }).text ?? '');
      }
      return '';
    })
    .join('');
}

function extractAssistantContent(
  assistantMsg: UIMessage,
  allMessages: UIMessage[],
): string {
  let t = extractAllTextParts(assistantMsg).trim();
  if (t) {
    return t;
  }
  const lastAssistant = [...allMessages].reverse().find((m) => m.role === 'assistant');
  if (lastAssistant) {
    t = extractAllTextParts(lastAssistant).trim();
  }
  return t;
}

function metaTime(m: UIMessage): string | null {
  const raw = (m.metadata as MessageMeta | undefined)?.createdAt;
  if (!raw) {
    return null;
  }
  return formatDateTimeRecife(raw);
}

export function ChatPanel() {
  const router = useRouter();
  const { user, logout } = useUser();
  const [mounted, setMounted] = useState(false);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loadingConvList, setLoadingConvList] = useState(true);
  const [switchingConv, setSwitchingConv] = useState(false);

  const [bootError, setBootError] = useState<string | null>(null);
  const [inlineError, setInlineError] = useState<string | null>(null);
  const [loadingBoot, setLoadingBoot] = useState(true);
  const [provider, setProvider] = useState<ProviderName>('groq');
  const [groqModelId, setGroqModelId] = useState(GROQ_DEFAULT_MODEL_ID);
  const [groqCustomModelId, setGroqCustomModelId] = useState('');
  const [groqModalOpen, setGroqModalOpen] = useState(false);
  const [input, setInput] = useState('');
  const [selectedConvIds, setSelectedConvIds] = useState<Set<string>>(() => new Set());
  const [recifeClock, setRecifeClock] = useState('');

  const token = typeof window !== 'undefined' ? getAccessToken() : null;

  useEffect(() => {
    setMounted(true);
  }, []);

  const effectiveModelForRequest = useMemo(() => {
    if (provider !== 'groq') {
      return undefined;
    }
    const custom = groqCustomModelId.trim();
    return custom || groqModelId;
  }, [provider, groqModelId, groqCustomModelId]);

  const conversationRef = useRef(conversation);
  const effectiveModelRef = useRef<string | undefined>(undefined);
  useEffect(() => {
    conversationRef.current = conversation;
  }, [conversation]);
  useEffect(() => {
    effectiveModelRef.current = effectiveModelForRequest;
  }, [effectiveModelForRequest]);

  const selectedGroqMeta = useMemo(
    () => GROQ_MODEL_OPTIONS.find((m) => m.id === groqModelId),
    [groqModelId],
  );

  const refreshConversations = useCallback(async (): Promise<Conversation[] | null> => {
    if (!workspace || !token) {
      return null;
    }
    const list = await apiRequest<Conversation[]>(
      `/chats/conversations?workspace_id=${encodeURIComponent(workspace.id)}`,
      { method: 'GET' },
      token,
    );
    setConversations(list);
    return list;
  }, [workspace, token]);

  const refreshMessages = useCallback(async () => {
    const cid = conversationRef.current?.id;
    if (!cid || !token) {
      return;
    }
    const rows = await apiRequest<Message[]>(
      `/chats/conversations/${cid}/messages`,
      { method: 'GET' },
      token,
    );
    return messagesToUiMessages(rows);
  }, [token]);

  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: '/api/chat',
        body: {
          provider: 'groq',
          model: effectiveModelForRequest,
        },
      }),
    [effectiveModelForRequest],
  );

  const { messages, setMessages, sendMessage, status, error } = useChat({
    transport,
    onFinish: async ({ message: assistantMsg, messages: allMessages, isError }) => {
      const convId = conversationRef.current?.id;
      const modelId = effectiveModelRef.current;
      if (!convId || !token) {
        return;
      }

      if (isError) {
        try {
          await refreshConversations();
        } catch {
          /* ignore */
        }
        return;
      }

      const content = extractAssistantContent(assistantMsg, allMessages);
      if (!content.trim()) {
        console.warn('[chat] Texto do assistente vazio ao persistir');
        try {
          await refreshConversations();
        } catch {
          /* ignore */
        }
        return;
      }

      try {
        await apiRequest<Message>(
          `/chats/conversations/${convId}/messages`,
          {
            method: 'POST',
            body: JSON.stringify({
              role: 'assistant',
              content,
              model: modelId,
              provider: 'groq',
            }),
          },
          token,
        );
      } catch (persistError) {
        console.error('Falha ao salvar resposta do assistente:', persistError);
      }

      try {
        const ui = await refreshMessages();
        if (ui) {
          setMessages(ui);
        }
        await refreshConversations();
      } catch (e) {
        console.error('Falha ao sincronizar mensagens:', e);
      }
    },
  });

  useEffect(() => {
    if (!groqModalOpen) {
      return;
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setGroqModalOpen(false);
      }
    };
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKey);
    };
  }, [groqModalOpen]);

  useEffect(() => {
    function tick() {
      // Usa timestamp UTC atual e converte para Recife
      const now = new Date();
      const utcTimestamp = Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        now.getUTCHours(),
        now.getUTCMinutes(),
        now.getUTCSeconds()
      );
      setRecifeClock(formatDateTimeRecife(new Date(utcTimestamp).toISOString()));
    }
    tick();
    const id = window.setInterval(tick, 30_000);
    return () => window.clearInterval(id);
  }, []);

  function handleLogout() {
    logout();
    router.push('/login');
    router.refresh();
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        if (!token) {
          throw new Error('Faça login antes de acessar o chat.');
        }

        const workspaces = await apiRequest<Workspace[]>(
          '/workspaces',
          { method: 'GET' },
          token,
        );

        if (!workspaces.length) {
          throw new Error('Nenhum workspace disponível.');
        }

        const ws = workspaces[0];
        setWorkspace(ws);

        const list = await apiRequest<Conversation[]>(
          `/chats/conversations?workspace_id=${encodeURIComponent(ws.id)}`,
          { method: 'GET' },
          token,
        );

        let active: Conversation;
        if (list.length === 0) {
          active = await apiRequest<Conversation>(
            '/chats/conversations',
            {
              method: 'POST',
              body: JSON.stringify({
                workspace_id: ws.id,
                title: 'Nova conversa',
              }),
            },
            token,
          );
          setConversations([active]);
        } else {
          setConversations(list);
          active = list[0];
        }

        setConversation(active);

        const rows = await apiRequest<Message[]>(
          `/chats/conversations/${active.id}/messages`,
          { method: 'GET' },
          token,
        );
        setMessages(messagesToUiMessages(rows));
      } catch (err) {
        setBootError(err instanceof Error ? err.message : 'Falha ao iniciar chat.');
      } finally {
        setLoadingBoot(false);
        setLoadingConvList(false);
      }
    }

    bootstrap().catch(console.error);
  }, [token, setMessages]);

  async function selectConversation(conv: Conversation) {
    if (!token || conv.id === conversation?.id) {
      return;
    }
    setSwitchingConv(true);
    setInlineError(null);
    try {
      setConversation(conv);
      const rows = await apiRequest<Message[]>(
        `/chats/conversations/${conv.id}/messages`,
        { method: 'GET' },
        token,
      );
      setMessages(messagesToUiMessages(rows));
    } catch (e) {
      setInlineError(e instanceof Error ? e.message : 'Falha ao abrir conversa.');
    } finally {
      setSwitchingConv(false);
    }
  }

  async function handleNewConversation() {
    if (!workspace || !token) {
      return;
    }
    setInlineError(null);
    try {
      const conv = await apiRequest<Conversation>(
        '/chats/conversations',
        {
          method: 'POST',
          body: JSON.stringify({
            workspace_id: workspace.id,
            title: 'Nova conversa',
          }),
        },
        token,
      );
      setConversations((prev) => [conv, ...prev]);
      setConversation(conv);
      setMessages([]);
    } catch (e) {
      setInlineError(e instanceof Error ? e.message : 'Falha ao criar conversa.');
    }
  }

  async function reconcileAfterDelete(list: Conversation[]) {
    setConversations(list);
    setSelectedConvIds(new Set());
    const curId = conversationRef.current?.id;
    if (!curId) {
      return;
    }
    const still = list.find((c) => c.id === curId);
    if (still) {
      setConversation(still);
      return;
    }
    if (list.length > 0) {
      const next = list[0];
      setConversation(next);
      if (!token) {
        return;
      }
      const rows = await apiRequest<Message[]>(
        `/chats/conversations/${next.id}/messages`,
        { method: 'GET' },
        token,
      );
      setMessages(messagesToUiMessages(rows));
      return;
    }
    if (workspace && token) {
      const conv = await apiRequest<Conversation>(
        '/chats/conversations',
        {
          method: 'POST',
          body: JSON.stringify({
            workspace_id: workspace.id,
            title: 'Nova conversa',
          }),
        },
        token,
      );
      setConversations([conv]);
      setConversation(conv);
      setMessages([]);
    }
  }

  async function deleteConversationById(id: string, e?: React.MouseEvent) {
    e?.stopPropagation();
    if (!token) {
      return;
    }
    if (!confirm('Excluir esta conversa?')) {
      return;
    }
    await apiRequest(
      `/chats/conversations/${encodeURIComponent(id)}`,
      { method: 'DELETE' },
      token,
    );
    const list = await refreshConversations();
    if (list) {
      await reconcileAfterDelete(list);
    }
  }

  async function deleteSelectedConversations() {
    if (!token || selectedConvIds.size === 0) {
      return;
    }
    if (!confirm(`Excluir ${selectedConvIds.size} conversa(s)?`)) {
      return;
    }
    await apiRequest(
      '/chats/conversations/delete-many',
      {
        method: 'POST',
        body: JSON.stringify({ conversation_ids: [...selectedConvIds] }),
      },
      token,
    );
    const list = await refreshConversations();
    if (list) {
      await reconcileAfterDelete(list);
    }
  }

  function toggleConvSelected(id: string, e?: React.SyntheticEvent) {
    e?.stopPropagation();
    setSelectedConvIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const userContent = input.trim();

    if (!conversation || !token || !userContent) {
      return;
    }

    if (provider !== 'groq') {
      setInlineError('Configure as chaves de API e ative OpenAI ou Gemini no projeto.');
      return;
    }

    setInlineError(null);

    try {
      await apiRequest<Message>(
        `/chats/conversations/${conversation.id}/messages`,
        {
          method: 'POST',
          body: JSON.stringify({
            role: 'user',
            content: userContent,
          }),
        },
        token,
      );
      const list = await refreshConversations();
      if (list) {
        const me = list.find((c) => c.id === conversation.id);
        if (me) {
          setConversation(me);
        }
      }
    } catch (persistError) {
      setInlineError(
        persistError instanceof Error
          ? persistError.message
          : 'Falha ao salvar mensagem do usuário.',
      );
      return;
    }

    try {
      await sendMessage({
        text: userContent,
      });
      setInput('');
    } catch (sendError) {
      setInlineError(
        friendlyChatErrorMessage(
          sendError instanceof Error ? sendError.message : 'Falha ao enviar mensagem para o modelo.',
        ),
      );
    }
  }

  if (loadingBoot) {
    return <div className="p-6">Inicializando...</div>;
  }

  if (bootError) {
    return (
      <div className="p-6">
        <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700">
          {bootError}
        </div>
      </div>
    );
  }

  const groqSummaryLabel = groqCustomModelId.trim()
    ? `Personalizado: ${groqCustomModelId.trim()}`
    : selectedGroqMeta?.title ?? effectiveModelForRequest;

  const displayError = error ? friendlyChatErrorMessage(error.message) : null;

  const groqModal =
    groqModalOpen && provider === 'groq' && mounted ? (
      <div
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        role="presentation"
        style={{ isolation: 'isolate' }}
      >
        <button
          type="button"
          className="absolute inset-0 bg-black/40 backdrop-blur-[1px]"
          aria-label="Fechar diálogo"
          onClick={() => setGroqModalOpen(false)}
        />
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="groq-modal-title"
          className="relative z-[101] flex max-h-[min(520px,82vh)] w-full max-w-md flex-col overflow-hidden rounded-2xl border border-zinc-200/80 bg-white shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex shrink-0 items-center justify-between border-b border-zinc-100 px-4 py-3">
            <h2 id="groq-modal-title" className="pr-2 text-base font-semibold text-zinc-900">
              Escolher modelo Groq
            </h2>
            <button
              type="button"
              onClick={() => setGroqModalOpen(false)}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-lg leading-none text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900"
              aria-label="Fechar"
            >
              ×
            </button>
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-3">
            <p className="mb-3 text-xs leading-relaxed text-zinc-600">
              A etiqueta <strong>Padrão</strong> indica o modelo usado se não mudar nada. As alterações
              aplicam-se ao fechar.
            </p>

            <ul className="space-y-2">
              {GROQ_MODEL_OPTIONS.map((opt) => {
                const isDefault = opt.id === GROQ_DEFAULT_MODEL_ID;
                return (
                  <li key={opt.id}>
                    <label
                      className={`flex cursor-pointer gap-2.5 rounded-xl border p-2.5 text-left transition-colors ${
                        groqModelId === opt.id
                          ? 'border-emerald-600 bg-emerald-50/80'
                          : 'border-zinc-200 bg-zinc-50/50 hover:border-zinc-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="groq-model-modal"
                        className="mt-0.5 h-4 w-4 shrink-0 accent-emerald-700"
                        checked={groqModelId === opt.id}
                        onChange={() => setGroqModelId(opt.id)}
                      />
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="text-sm font-medium text-zinc-900">{opt.title}</span>
                          {isDefault ? (
                            <span className="rounded bg-emerald-200/90 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-emerald-900">
                              Padrão
                            </span>
                          ) : null}
                        </div>
                        <p className="mt-0.5 text-xs leading-snug text-zinc-600">{opt.summary}</p>
                        <p className="mt-1 break-all font-mono text-[10px] text-zinc-400">{opt.id}</p>
                      </div>
                    </label>
                  </li>
                );
              })}
            </ul>

            <div className="mt-3 rounded-lg border border-dashed border-zinc-300 bg-white p-2.5">
              <label htmlFor="groq-custom-model" className="text-xs font-medium text-zinc-800">
                ID personalizado (opcional)
              </label>
              <p className="mt-0.5 text-[11px] text-zinc-500">
                Deixe vazio para usar o modelo selecionado acima.
              </p>
              <input
                id="groq-custom-model"
                type="text"
                value={groqCustomModelId}
                onChange={(e) => setGroqCustomModelId(e.target.value)}
                placeholder="ex.: llama-3.1-8b-instant"
                className="mt-1.5 w-full rounded-md border border-zinc-300 px-2 py-1.5 font-mono text-xs"
                autoComplete="off"
              />
            </div>

            {selectedGroqMeta ? (
              <details className="mt-2 rounded-lg border border-zinc-100 bg-zinc-50/80 p-2 text-xs text-zinc-600">
                <summary className="cursor-pointer font-medium text-zinc-800">
                  Texto completo sobre “{selectedGroqMeta.title}”
                </summary>
                <p className="mt-2 leading-relaxed">{selectedGroqMeta.description}</p>
              </details>
            ) : null}
          </div>

          <div className="flex shrink-0 justify-end gap-2 border-t border-zinc-100 bg-zinc-50/50 px-4 py-3">
            <button
              type="button"
              onClick={() => setGroqModalOpen(false)}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-800 hover:bg-zinc-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => setGroqModalOpen(false)}
              className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
            >
              OK
            </button>
          </div>
        </div>
      </div>
    ) : null;

  return (
    <div className="mx-auto flex h-[100dvh] min-h-0 w-full max-w-6xl flex-col px-3 py-3 sm:px-4">
      <header className="mb-2 flex shrink-0 flex-wrap items-start justify-between gap-2 border-b border-zinc-200/80 pb-2">
        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold sm:text-xl">SaaS Chatbot AI</h1>
          <p className="truncate text-xs text-zinc-500">{workspace?.name ?? '-'}</p>
        </div>
        <div className="flex shrink-0 gap-2">
          {user?.is_admin && (
            <button
              type="button"
              onClick={() => router.push('/admin')}
              className="shrink-0 rounded-lg border border-purple-300 bg-purple-50 px-3 py-1.5 text-sm font-medium text-purple-800 hover:bg-purple-100"
            >
              Admin
            </button>
          )}
          <button
            type="button"
            onClick={handleLogout}
            className="shrink-0 rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm font-medium text-zinc-800 hover:bg-zinc-50"
          >
            Sair
          </button>
        </div>
      </header>

      <div className="mb-2 flex min-h-0 flex-1 flex-col gap-2 md:flex-row md:gap-3">
        {/* Histórico de conversas */}
        <aside className="flex max-h-40 shrink-0 flex-col overflow-hidden rounded-xl border border-zinc-200 bg-zinc-50/80 md:max-h-none md:w-56 md:shrink-0">
          <div className="flex flex-wrap items-center justify-between gap-1 border-b border-zinc-200/80 px-2 py-1.5">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-600">
              Conversas
            </span>
            <div className="flex flex-wrap items-center justify-end gap-1">
              {selectedConvIds.size > 0 ? (
                <button
                  type="button"
                  onClick={() => void deleteSelectedConversations()}
                  className="rounded-md border border-red-200 bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-800 hover:bg-red-100 sm:px-2 sm:text-[11px]"
                  disabled={!token || status === 'streaming'}
                >
                  <span className="hidden sm:inline">Excluir </span>({selectedConvIds.size})
                </button>
              ) : null}
              <button
                type="button"
                onClick={handleNewConversation}
                className="rounded-md bg-zinc-900 px-1.5 py-0.5 text-[10px] font-medium text-white hover:bg-zinc-800 sm:px-2 sm:text-[11px]"
                disabled={!token || status === 'streaming'}
              >
                <span className="hidden sm:inline">+ Nova</span>
                <span className="sm:hidden">+</span>
              </button>
            </div>
          </div>
          <nav
            className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-1 py-1"
            aria-label="Histórico de conversas"
          >
            {loadingConvList ? (
              <p className="px-2 py-2 text-xs text-zinc-500">A carregar…</p>
            ) : (
              <ul className="space-y-0.5">
                {conversations.map((c) => {
                  const active = conversation?.id === c.id;
                  const preview = formatShortRecife(c.updated_at);
                  return (
                    <li key={c.id} className="flex min-h-0 items-stretch gap-0.5">
                      <label className="flex shrink-0 cursor-pointer items-center px-0.5">
                        <input
                          type="checkbox"
                          checked={selectedConvIds.has(c.id)}
                          onChange={(e) => toggleConvSelected(c.id, e)}
                          onClick={(e) => e.stopPropagation()}
                          className="h-3 w-3 rounded border-zinc-400 sm:h-3.5 sm:w-3.5"
                          aria-label={`Selecionar conversa ${c.title || c.id}`}
                        />
                      </label>
                      <button
                        type="button"
                        onClick={() => selectConversation(c)}
                        disabled={switchingConv || status === 'streaming'}
                        className={`min-w-0 flex-1 rounded-lg px-1.5 py-1 text-left text-xs transition-colors sm:px-2 sm:py-1.5 sm:text-sm ${
                          active
                            ? 'bg-emerald-100 font-medium text-emerald-950'
                            : 'text-zinc-800 hover:bg-white'
                        }`}
                      >
                        <span className="line-clamp-1 sm:line-clamp-2">{c.title || 'Conversa'}</span>
                        <span className="mt-0.5 block text-[9px] font-normal text-zinc-500 sm:text-[10px]">
                          {preview}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={(e) => void deleteConversationById(c.id, e)}
                        disabled={switchingConv || status === 'streaming'}
                        className="shrink-0 rounded-lg px-1 py-1 text-xs text-zinc-500 hover:bg-red-50 hover:text-red-700 sm:px-1.5 sm:py-1"
                        title="Excluir conversa"
                        aria-label="Excluir conversa"
                      >
                        <span className="hidden sm:inline">×</span>
                        <span className="sm:hidden">×</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </nav>
        </aside>

        {/* Área principal */}
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <div className="mb-2 flex shrink-0 flex-wrap items-center gap-x-2 gap-y-1 text-xs sm:text-sm">
            {inlineError ? (
              <div className="w-full rounded-lg border border-red-200 bg-red-50 px-1.5 py-1 text-xs text-red-800 sm:px-2 sm:py-1.5">
                {inlineError}
              </div>
            ) : null}

            <label htmlFor="chat-provider" className="sr-only">
              Provedor de IA
            </label>
            <select
              id="chat-provider"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value as ProviderName);
                setInlineError(null);
              }}
              className="rounded-lg border border-zinc-300 bg-white px-1.5 py-1 text-xs sm:px-2 sm:py-1 sm:text-sm"
              disabled={status === 'streaming'}
            >
              <option value="groq">Groq</option>
              <option value="openai" disabled>
                OpenAI (em breve)
              </option>
              <option value="google" disabled>
                Gemini (em breve)
              </option>
            </select>

            {provider === 'groq' ? (
              <>
                <span className="text-zinc-300">·</span>
                <span
                  className="max-w-[6rem] truncate text-[11px] text-zinc-600 sm:max-w-xs sm:text-xs sm:text-sm"
                  title={groqSummaryLabel}
                >
                  {groqSummaryLabel}
                </span>
                <button
                  type="button"
                  onClick={() => setGroqModalOpen(true)}
                  className="rounded-lg border border-emerald-600 bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-900 hover:bg-emerald-100 sm:px-2 sm:py-1 sm:text-xs sm:text-sm"
                  disabled={status === 'streaming'}
                >
                  <span className="hidden sm:inline">Modelos…</span>
                  <span className="sm:hidden">⋯</span>
                </button>
              </>
            ) : (
              <span className="text-[11px] text-amber-800 sm:text-xs">Use Groq até configurar outros provedores.</span>
            )}
          </div>

          {switchingConv ? (
            <p className="mb-1 text-[11px] text-zinc-500 sm:text-xs">A abrir conversa…</p>
          ) : null}

          <main className="flex min-h-0 flex-1 flex-col gap-2">
            <div className="min-h-0 flex-1 overflow-y-auto rounded-2xl border border-zinc-200 bg-white p-2 shadow-sm sm:p-3 sm:p-4">
              <div className="space-y-4">
                {messages.map((message) => {
                  const t = metaTime(message);
                  return (
                    <div
                      key={message.id}
                      className={
                        message.role === 'user'
                          ? 'ml-auto max-w-[min(100%,90%)] rounded-2xl bg-zinc-900 p-2 text-white sm:p-3 sm:p-4'
                          : 'mr-auto max-w-[min(100%,90%)] rounded-2xl bg-zinc-100 p-2 text-zinc-900 sm:p-3 sm:p-4'
                      }
                    >
                      <div className="mb-1 flex flex-wrap items-center justify-between gap-1">
                        <span className="text-[10px] uppercase tracking-wide opacity-70">
                          {message.role === 'user' ? 'usuário' : 'assistente'}
                        </span>
                        {t ? (
                          <time
                            dateTime={(message.metadata as MessageMeta)?.createdAt}
                            className={
                              message.role === 'user'
                                ? 'text-[10px] tabular-nums text-zinc-400'
                                : 'text-[10px] tabular-nums text-zinc-500'
                            }
                          >
                            {t}
                          </time>
                        ) : null}
                      </div>
                      <div className="whitespace-pre-wrap text-xs leading-relaxed sm:text-sm">
                        {extractAllTextParts(message)}
                      </div>
                    </div>
                  );
                })}

                {displayError ? (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-2 text-xs text-amber-950 sm:p-3 sm:text-sm">
                    {displayError}
                  </div>
                ) : null}
              </div>
            </div>

            <form onSubmit={onSubmit} className="flex shrink-0 gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua mensagem…"
                className="min-h-[40px] flex-1 resize-y rounded-xl border border-zinc-300 p-2 text-xs outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-200 sm:min-h-[48px] sm:p-2.5 sm:text-sm"
                disabled={status === 'streaming' || provider !== 'groq' || switchingConv}
                rows={2}
              />
              <button
                type="submit"
                className="self-end rounded-xl bg-zinc-900 px-3 py-2 text-xs font-medium text-white hover:bg-zinc-800 disabled:opacity-50 sm:px-4 sm:py-2.5 sm:text-sm"
                disabled={
                  status === 'streaming' || !input.trim() || provider !== 'groq' || switchingConv
                }
              >
                {status === 'streaming' ? '…' : 'Enviar'}
              </button>
            </form>
          </main>
        </div>
      </div>

      {mounted && groqModal ? createPortal(groqModal, document.body) : null}
    </div>
  );
}
