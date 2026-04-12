import {
  convertToModelMessages,
  streamText,
  type UIMessage,
  type LanguageModelUsage,
} from 'ai';
import {
  getLanguageModel,
  type ProviderName,
  resolveProviderConfig,
} from '@/lib/ai/provider';

export const runtime = 'nodejs';

type ChatRequestBody = {
  messages?: UIMessage[];
  provider?: ProviderName;
  model?: string;
};

function buildSystemPrompt(): string {
  return [
    'Você é um assistente de um SaaS de chatbot com IA.',
    'Responda de forma clara, objetiva e confiável.',
    'Se não souber algo, diga explicitamente.',
    'Não invente dados do usuário, billing, banco de dados ou documentos inexistentes.',
  ].join(' ');
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as ChatRequestBody;

    if (!Array.isArray(body.messages) || body.messages.length === 0) {
      return Response.json(
        { error: 'messages é obrigatório' },
        { status: 422 },
      );
    }

    const providerConfig = resolveProviderConfig({
      provider: body.provider,
      model: body.model,
    });

    const model = getLanguageModel(providerConfig);
    const modelMessages = convertToModelMessages(body.messages);

    const result = streamText({
      model,
      system: buildSystemPrompt(),
      messages: modelMessages,
      temperature: 0.3,
      maxOutputTokens: 1200,
      maxRetries: 2,
    });

    // Capture usage data to include in response headers
    let usageData: LanguageModelUsage | null = null;

    return result.toUIMessageStreamResponse({
      originalMessages: body.messages,
      headers: {
        'X-LLM-Provider': providerConfig.provider,
        'X-LLM-Model': providerConfig.model ?? '',
      },
      onFinish: async ({ messages }) => {
        // Capture usage data from the stream result
        try {
          usageData = await result.usage;
        } catch (e) {
          console.error('[api/chat] Failed to get usage:', e);
        }
      },
      onError: () =>
        'A conexão com o modelo falhou (rede ou tempo esgotado). Experimente outro modelo em «Modelos…» ou tente novamente em instantes.',
    });
  } catch (error) {
    console.error('[api/chat]', error);
    return Response.json(
      { error: 'Não foi possível processar o pedido.' },
      { status: 500 },
    );
  }
}