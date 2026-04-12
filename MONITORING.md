# 📊 Monitoramento - Prometheus + Grafana + Loki

Este documento descreve como usar o stack de monitoramento implementado no SaaS Chatbot AI.

## 🎯 O que foi adicionado

### 1. Prometheus (Métricas)
- **URL**: http://localhost/prometheus/
- **Função**: Coleta métricas da API, banco de dados e Redis
- **Métricas disponíveis**:
  - `http_requests_total` - Total de requisições HTTP
  - `http_request_duration_seconds` - Latência das requisições
  - `llm_requests_total` - Chamadas ao LLM por provedor/modelo
  - `llm_tokens_total` - Tokens consumidos (prompt/completion/total)
  - `llm_request_duration_seconds` - Latência das chamadas LLM
  - `llm_fallback_total` - Taxa de fallback entre provedores
  - `llm_cost_usd` - Custo estimado das chamadas
  - `errors_total` - Erros por tipo
  - `active_users` - Usuários ativos
  - Métricas do PostgreSQL (via postgres_exporter)
  - Métricas do Redis (via redis_exporter)

### 2. Grafana (Visualização)
- **URL**: http://localhost/grafana/
- **Login padrão**: admin / admin
- **Datasources configurados**:
  - Prometheus (métricas)
  - Loki (logs)
- **Recursos**:
  - Dashboards pré-configurados (quando criados)
  - Alertas configuráveis
  - Visualização de logs em tempo real

### 3. Loki (Logs)
- **URL interno**: http://loki:3100
- **Função**: Agregação e indexação de logs
- **Integração**: Via **Promtail** (coletor de logs). O Promtail lê os logs de todos os containers Docker automaticamente através do socket `/var/run/docker.sock` e os envia para o Loki.

## 🚀 Como usar

### 1. Subir os serviços

```bash
docker compose -f docker-compose.prod.yml up -d
```

*Nota: Não é mais necessário instalar o plugin de log do Docker, pois agora usamos o Promtail, que é mais robusto e não trava os containers se o Loki estiver fora do ar.*

### 2. Acessar o Grafana

1. Abra http://localhost/grafana/
2. Login: `admin` / `admin` (ou valores definidos em `GRAFANA_ADMIN_PASSWORD`)
3. Na primeira vez, será solicitado trocar a senha

### 3. Criar Dashboards

#### Dashboard de LLM (Exemplo)

1. No Grafana: **Create** → **Dashboard**
2. Adicione painéis com as seguintes queries:

**Taxa de sucesso das respostas:**
```promql
rate(llm_requests_total{status="success"}[5m]) / rate(llm_requests_total[5m])
```

**Latência média (p95):**
```promql
histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))
```

**Tokens por provedor:**
```promql
sum by (provider) (rate(llm_tokens_total{token_type="total"}[5m]))
```

**Taxa de fallback:**
```promql
rate(llm_fallback_total[5m])
```

**Custo estimado:**
```promql
sum by (provider) (llm_cost_usd)
```

#### Dashboard de Infraestrutura

**CPU/Memória dos containers:**
```promql
container_cpu_usage_seconds_total
container_memory_usage_bytes
```

**Conexões PostgreSQL:**
```promql
pg_stat_activity_count
```

**Operações Redis:**
```promql
redis_commands_processed_total
```

## 📁 Arquivos de configuração

```
infra/
├── prometheus/
│   └── prometheus.yml          # Configuração do Prometheus
├── grafana/
│   └── datasources/
│       └── datasources.yml     # Configuração dos datasources
└── loki/
    └── loki-config.yml         # Configuração do Loki
```

## 🔐 Segurança (Produção)

### 1. Proteger o Prometheus

Adicione autenticação básica no Nginx:

```nginx
location /prometheus/ {
    auth_basic "Prometheus";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ... resto da config
}
```

### 2. Restringir acesso ao Grafana

Configure `GF_SECURITY_ADMIN_PASSWORD` no `.env`:

```env
GRAFANA_ADMIN_PASSWORD=senha_forte_aqui
```

### 3. HTTPS

Use certificados SSL no Nginx para todas as rotas.

## 📈 Métricas de Negócio

Para registrar métricas customizadas no código Python:

```python
from app.core.metrics import record_llm_request, record_fallback, record_error

# Registrar chamada LLM
record_llm_request(
    provider="groq",
    model="llama-3.1-70b",
    duration=1.5,
    tokens_prompt=100,
    tokens_completion=150,
    success=True
)

# Registrar fallback
record_fallback(
    from_provider="openai",
    to_provider="groq",
    reason="rate_limit"
)

# Registrar erro
record_error(error_type="timeout", endpoint="/api/v1/chats")
```

## 🔍 Logs com Loki

### Ver logs no Grafana

1. Acesse **Explore** no menu lateral
2. Selecione datasource **Loki**
3. Filtre por labels:
   - `{service_name="saas_api_prod"}` - Logs da API
   - `{service_name="saas_web_prod"}` - Logs do frontend
   - `{service_name="saas_db_prod"}` - Logs do banco

### Queries de exemplo (LogQL)

**Erros na API:**
```logql
{service_name="saas_api_prod"} |= "ERROR"
```

**Requisições lentas:**
```logql
{service_name="saas_api_prod"} |~ "duration.*[5-9]\.[0-9]+s"
```

**Logs de LLM:**
```logql
{service_name="saas_api_prod"} |= "llm" or "chat"
```

## 🚨 Alertas (opcional)

Para configurar alertas no Prometheus/Alertmanager, crie um arquivo `alert.rules`:

```yaml
groups:
  - name: saas_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erro alta detectada"
          
      - alert: LLMLatencyHigh
        expr: histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m])) > 5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Latência do LLM acima de 5s"
```

## 📊 Dashboards recomendados

### 1. Dashboard de LLM

| Métrica | Query | Tipo |
|---------|-------|------|
| Requisições/min | `rate(llm_requests_total[5m])` | Graph |
| Latência p99 | `histogram_quantile(0.99, ...)` | Graph |
| Tokens/hora | `increase(llm_tokens_total[1h])` | Stat |
| Taxa fallback | `rate(llm_fallback_total[5m])` | Graph |
| Custo diário | `increase(llm_cost_usd[24h])` | Stat |

### 2. Dashboard de API

| Métrica | Query | Tipo |
|---------|-------|------|
| Requisições/seg | `rate(http_requests_total[1m])` | Graph |
| Latência p95 | `histogram_quantile(0.95, ...)` | Graph |
| Taxa erro 5xx | `rate(http_requests_total{status=~"5.."}[5m])` | Graph |
| Usuários ativos | `active_users` | Stat |

---

## 📊 Dashboards Pré-Configurados

O Grafana vem com **3 dashboards pré-configurados** automaticamente provisionados:

### 1. 🤖 LLM / Chatbot Metrics (`llm-dashboard`)
**URL**: http://localhost/grafana/d/llm-dashboard

**Painéis incluídos**:
- **Requisições por Provedor/Modelo** - Gráfico de requisições/segundo
- **Latência P95** - Gauge com alerta visual (>5s = vermelho)
- **Tokens por Provedor** - Gráfico de pizza (donut)
- **Taxa de Tokens** - Comparativo prompt vs completion
- **Taxa de Sucesso** - Percentual de chamadas bem-sucedidas
- **Taxa de Fallback** - Percentual de fallbacks
- **Custo Estimado** - Custo em USD por provedor

**Como interpretar**:
- Taxa de sucesso < 95% → investigar erros
- Latência P95 > 5s → considerar fallback para outro provedor
- Tokens de completion >> tokens de prompt → modelo está "falador"

---

### 2. 🚀 API Performance (`api-dashboard`)
**URL**: http://localhost/grafana/d/api-dashboard

**Painéis incluídos**:
- **Usuários Ativos** - Total em tempo real
- **Requisições/seg** - Throughput da API
- **Taxa de Erro 5xx** - Erros críticos (alerta > 1%)
- **Latência API P95** - Tempo de resposta da API
- **Requisições por Endpoint** - Distribuição por rota
- **Latência por Endpoint** - P50 e P95 por endpoint
- **Distribuição de Status HTTP** - 200, 400, 500
- **Erros por Tipo** - Categorização de erros

**Como interpretar**:
- Latência P95 > 500ms → verificar banco/LLM
- Erro 5xx > 0.1% → investigar imediatamente
- Usuários ativos caindo → possível problema de acesso

---

### 3. 🖥️ System Overview (`system-dashboard`)
**URL**: http://localhost/grafana/d/system-dashboard

**Painéis incluídos**:
- **Conexões PostgreSQL (%)** - Uso das conexões (alerta > 80%)
- **Memória Redis (%)** - Uso de memória (alerta > 80%)
- **Redis Hit Ratio (%)** - Eficiência do cache (ideal > 90%)
- **Redis Ops/sec** - Operações por segundo
- **Conexões PostgreSQL** - Ativas vs máximo
- **Memória Redis** - Usada vs limite
- **PostgreSQL Cache Miss** - Taxa de cache miss (ideal < 5%)

**Como interpretar**:
- Conexões PostgreSQL > 80% → aumentar pool ou otimizar queries
- Redis hit ratio < 80% → cache ineficiente
- PostgreSQL cache miss alto → aumentar shared_buffers

---

## 🚨 Alertas Configurados

O Grafana vem com **5 alertas pré-configurados**:

| Alerta | Condição | Severidade | Descrição |
|--------|----------|------------|-----------|
| **Taxa de Erro API Alta** | Erro 5xx > 10% | 🔴 Critical | Taxa de erro da API acima de 10% |
| **Latência LLM Alta** | P95 > 5 segundos | 🟡 Warning | LLM muito lento |
| **Taxa de Fallback Alta** | Fallback > 20% | 🟡 Warning | Muitos fallbacks indicam instabilidade |
| **Conexões PostgreSQL Altas** | Uso > 80% | 🔴 Critical | Risco de esgotar conexões |
| **Memória Redis Alta** | Uso > 80% | 🟡 Warning | Cache próximo do limite |

### Configurar Notificações de Alertas

1. Acesse: **Alerting** → **Contact Points**
2. Clique em **New contact point**
3. Escolha o tipo: Email, Slack, Discord, PagerDuty, etc.
4. Configure os detalhes (ex: webhook do Slack)
5. Vá em **Notification Policies** e associe aos alertas

**Exemplo - Slack**:
```yaml
Name: Slack Alerts
Integration: Slack
Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
Title: "Alerta: {{ .CommonLabels.alertname }}"
Text: "{{ .CommonAnnotations.summary }}"
```

---

## 🔍 Como Observar (Guia Prático)

### Cenário 1: Usuários relatam lentidão
1. Abra o dashboard **🚀 API Performance**
2. Verifique **Latência API P95**:
   - Se > 500ms → problema na API
   - Se normal → verificar LLM
3. Abra **🤖 LLM / Chatbot Metrics**
4. Verifique **Latência LLM P95**:
   - Se > 5s → fallback ativo ou provedor lento
   - Verifique **Taxa de Fallback**
5. Abra **🖥️ System Overview**
6. Verifique **Conexões PostgreSQL** e **Memória Redis**

### Cenário 2: Taxa de erro alta
1. Dashboard **🚀 API Performance** → **Taxa de Erro 5xx**
2. Verifique **Distribuição de Status HTTP**
3. Verifique **Erros por Tipo** no painel inferior
4. Clique no erro para ver detalhes no Loki (logs)

### Cenário 3: Custo LLM excessivo
1. Dashboard **🤖 LLM / Chatbot Metrics**
2. Verifique **Custo Estimado por Provedor**
3. Verifique **Tokens por Provedor**
4. Compare **Taxa de Tokens** (prompt vs completion)
5. Identifique qual provedor está mais caro

### Cenário 4: Queda de performance
1. Verifique todos os 3 dashboards
2. Olhe para tendências nos últimos 30 minutos
3. Verifique se algum alerta foi disparado (🔔 no menu)
4. Check logs no Loki para identificar causa raiz

---

## 🛠️ Troubleshooting

### Métricas não aparecem

1. Verifique se o Prometheus está acessível:
   ```bash
   docker logs saas_prometheus_prod
   ```

2. Verifique targets no Prometheus:
   http://localhost/prometheus/targets

3. Verifique o endpoint /metrics da API:
   ```bash
   curl http://localhost/api/v1/metrics
   ```

### Logs não aparecem no Loki

1. Verifique configuração do driver de log
2. Instale o plugin Loki para Docker:
   ```bash
   docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
   ```
3. Reinicie os containers

## 📚 Recursos adicionais

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [Loki Docs](https://grafana.com/docs/loki/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
