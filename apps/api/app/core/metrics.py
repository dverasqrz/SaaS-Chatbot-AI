"""Métricas Prometheus para monitoramento da API."""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.registry import REGISTRY

# Informações da aplicação
app_info = Info('saas_chatbot', 'Informações da aplicação SaaS Chatbot AI')

# Métricas de requisições HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

# Métricas de LLM
llm_requests_total = Counter(
    'llm_requests_total',
    'Total de requisições ao LLM',
    ['provider', 'model', 'status']
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'Latência das requisições ao LLM em segundos',
    ['provider', 'model'],
    buckets=[.1, .25, .5, .75, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 10.0]
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total de tokens consumidos',
    ['provider', 'model', 'token_type']  # token_type: prompt, completion, total
)

llm_fallback_total = Counter(
    'llm_fallback_total',
    'Total de fallbacks entre provedores',
    ['from_provider', 'to_provider', 'reason']
)

# Métricas de negócio
active_users = Gauge(
    'active_users',
    'Número de usuários ativos no momento'
)

total_conversations = Gauge(
    'total_conversations',
    'Total de conversas no sistema'
)

total_messages = Gauge(
    'total_messages',
    'Total de mensagens no sistema'
)

# Métricas de erro
errors_total = Counter(
    'errors_total',
    'Total de erros por tipo',
    ['error_type', 'endpoint']
)

# Custo estimado (custo por 1K tokens)
llm_cost_usd = Counter(
    'llm_cost_usd',
    'Custo estimado em USD das chamadas LLM',
    ['provider', 'model']
)

# Taxa de sucesso
response_success_rate = Gauge(
    'response_success_rate',
    'Taxa de sucesso das respostas (0-1)',
    ['provider']
)


def set_app_info(version: str = "1.0.0", environment: str = "production"):
    """Define informações da aplicação."""
    app_info.info({
        'version': version,
        'environment': environment
    })


def record_llm_request(provider: str, model: str, duration: float, tokens_prompt: int = 0, tokens_completion: int = 0, success: bool = True):
    """Registra métricas de uma requisição LLM."""
    status = 'success' if success else 'error'
    llm_requests_total.labels(provider=provider, model=model, status=status).inc()
    llm_request_duration_seconds.labels(provider=provider, model=model).observe(duration)
    
    if tokens_prompt > 0:
        llm_tokens_total.labels(provider=provider, model=model, token_type='prompt').inc(tokens_prompt)
    if tokens_completion > 0:
        llm_tokens_total.labels(provider=provider, model=model, token_type='completion').inc(tokens_completion)
    if tokens_prompt > 0 or tokens_completion > 0:
        llm_tokens_total.labels(provider=provider, model=model, token_type='total').inc(tokens_prompt + tokens_completion)


def record_fallback(from_provider: str, to_provider: str, reason: str):
    """Registra um fallback entre provedores."""
    llm_fallback_total.labels(from_provider=from_provider, to_provider=to_provider, reason=reason).inc()


def record_error(error_type: str, endpoint: str = "unknown"):
    """Registra um erro."""
    errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
