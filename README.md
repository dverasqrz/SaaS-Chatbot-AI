# SaaS Chatbot AI - Plataforma Completa

Uma plataforma moderna de chatbot IA com arquitetura SaaS, construída com as melhores tecnologias do mercado para oferecer uma experiência conversacional robusta e escalável.

## 🚀 Stack Tecnológico

### Frontend
- **Next.js 15** com App Router - Performance e otimização de ponta
- **TypeScript** - Tipagem segura e melhor DX
- **TailwindCSS** - Design system moderno e responsivo
- **Vercel AI SDK** - Integração fluida com múltiplos provedores de IA
- **React Hook Form** - Formulários otimizados

### Backend
- **FastAPI** - API REST de alta performance
- **SQLModel** - ORM moderno com Pydantic
- **PostgreSQL** - Banco de dados robusto e escalável
- **Redis** - Cache e gerenciamento de sessões
- **Pydantic** - Validação de dados automática

### DevOps & Infraestrutura
- **Docker & Docker Compose** - Containerização consistente
- **Nginx** - Proxy reverso e load balancing
- **Ambientes isolados** - Desenvolvimento e produção
- **Prometheus + Grafana + Loki + Promtail** - Monitoramento e observabilidade completa

## 🎯 Funcionalidades

### Core Features
- ✅ **Múltiplos Provedores de IA** - OpenAI, Gemini, Groq, Together AI
- ✅ **Geração Automática de Títulos** - Títulos inteligentes baseados no conteúdo
- ✅ **Sistema de Workspaces** - Multi-inquilino nativo
- ✅ **Histórico Completo** - Conversas persistidas com metadata
- ✅ **Interface Responsiva** - Experiência otimizada para todos os dispositivos
- ✅ **Fuso Horário Inteligente** - Suporte a timezone de Recife (PE)
- ✅ **Painel Administrativo** - Gerenciamento completo de usuários e sistema
- ✅ **Setup Automático** - Primeiro usuário vira admin automaticamente
- ✅ **Controle de Acesso** - Sistema de privilégios e gerenciamento de contas
- ✅ **Monitoramento** - Status online e consumo de tokens em tempo real

### Technical Features
- 🔐 **Autenticação Segura** - JWT-based authentication
- 🔄 **Hot Reload** - Desenvolvimento ágil
- 📊 **API Documentation** - OpenAPI/Swagger integrado
- 🏥 **Health Checks** - Monitoramento de saúde da aplicação
- 🚀 **Deploy Ready** - Configuração para produção

## 🛠️ Quick Start

### Pré-requisitos
- Docker e Docker Compose instalados
- Node.js 18+ (para desenvolvimento local)
- Python 3.11+ (para desenvolvimento local)

### 1. Configuração do Ambiente
```bash
# Clone o repositório
git clone <repository-url>
cd saas-chatbot-ai-docker-prod

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API
```

### 2. Desenvolvimento Local
```bash
# Suba todos os serviços
docker compose -f docker-compose.prod.yml up -d --build

# Acesse os serviços
# Frontend: http://localhost:3000/register
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
# Grafana: http://localhost/grafana/ (admin/admin)
# Prometheus: http://localhost/prometheus/
```

### 3. Fluxo de Teste
1. Abra `/register` e crie sua conta
2. **O primeiro usuário será automaticamente administrador** 
3. Faça login para acessar o dashboard
4. Configure seu provedor de IA preferido
5. Comece a conversar!

### 4. Acesso Administrativo
**Acesso automático para o primeiro usuário:**
- Ao criar a primeira conta, você recebe privilégios de administrador
- Após o login, o botão **"Admin"** (roxo) aparecerá no header
- Acesse `/admin` para gerenciar usuários e sistema

**Para usuários posteriores:**
- Apenas usuários com privilégios de admin podem acessar o painel
- Outros admins podem promover usuários através do painel administrativo

## 🔐 Administração

### Painel Administrativo
O sistema inclui um painel completo para administradores:

- **Dashboard com Estatísticas**: Total de usuários, usuários ativos, tokens utilizados
- **Gerenciamento de Usuários**: Listar, criar, editar, remover usuários
- **Controle de Acesso**: Ativar/desativar usuários, promover/demotionar admins
- **Monitoramento**: Status online/offline, consumo de tokens por usuário

### Funcionalidades Admin
- ✅ **CRUD Completo** - Criar, ler, atualizar, deletar usuários
- ✅ **Controle de Status** - Ativar/desativar contas
- ✅ **Gestão de Privilégios** - Promover usuários a administradores
- ✅ **Monitoramento em Tempo Real** - Status online e consumo de tokens
- ✅ **Segurança** - Proteção contra auto-desativação e remoção

### Acesso Admin
- Apenas usuários com `is_admin = true` acessam `/admin`
- Link admin visível apenas para administradores no header principal
- Todas as rotas admin protegidas com verificação de privilégios

## 🏗️ Arquitetura

```
graph TD
    User --- Nginx
    Nginx -- "/api/v1" --> API
    Nginx -- "/" --> WebApp
    Nginx -- "/grafana" --> Grafana
    API -- Metrics --> Prometheus
    API -- Logs --> Promtail
    Promtail -- Logs --> Loki
    Prometheus -- Metrics --> Grafana
    Loki -- Logs --> Grafana
    API -- Reads/Writes --> PostgreSQL
    WebApp -- API Calls --> API
```

A arquitetura do sistema é modular e conteinerizada, facilitando o desenvolvimento, a implantação e o escalonamento. Os principais componentes são:

*   **Frontend (Next.js)**: Interface do usuário.
*   **Backend (FastAPI)**: API RESTful com lógica de negócios, agora organizada em uma **camada de serviços** (`AuthService`, `ChatService`, `WorkspaceService`, `AdminService`) para baixo acoplamento.
*   **Banco de Dados (PostgreSQL)**: Persistência de dados.
*   **Redis**: Cache e gerenciamento de sessões.
*   **Nginx**: Reverse proxy e balanceador de carga.
*   **Monitoramento (Prometheus, Grafana, Loki, Promtail)**: Observabilidade completa do sistema. O **Promtail** é responsável por coletar logs de todos os contêineres e enviá-los para o Loki, garantindo robustez e desacoplamento.

## 📊 Monitoramento & Observabilidade

O projeto inclui um stack completo de monitoramento com **Prometheus + Grafana + Loki**.

### 🔗 URLs de Acesso

| Serviço | URL | Login Padrão |
|---------|-----|--------------|
| **Grafana** | http://localhost/grafana/ | admin / admin |
| **Prometheus** | http://localhost/prometheus/ | - |
| **App** | http://localhost | - |

### 📈 Métricas Coletadas

#### Métricas de Negócio (LLM)
- `llm_requests_total` - Total de chamadas por provedor/modelo
- `llm_tokens_total` - Tokens consumidos (prompt/completion/total)
- `llm_request_duration_seconds` - Latência das chamadas
- `llm_fallback_total` - Taxa de fallback entre provedores
- `llm_cost_usd` - Custo estimado das chamadas

#### Métricas de API
- `http_requests_total` - Requisições HTTP por endpoint
- `http_request_duration_seconds` - Latência da API
- `errors_total` - Erros por tipo
- `active_users` - Usuários ativos no momento

#### Métricas de Infraestrutura
- PostgreSQL: conexões, queries lentas, cache hits
- Redis: operações/sec, memory usage, hit ratio

### 🚨 Alertas (configuráveis)

O Grafana suporta alertas para:
- Taxa de erro > 10%
- Latência LLM > 5s
- Uso excessivo de tokens
- Queda de serviços

### 📚 Documentação Detalhada

Para mais detalhes sobre a configuração e uso do stack de monitoramento, consulte o arquivo `ARCHITECTURE.md`.

## 🚀 Deploy em Produção

### Configuração de Produção
```bash
# Configure para produção
cp .env.example .env
# Ajuste variáveis de ambiente

# Suba em modo produção
docker compose -f docker-compose.prod.yml up --build -d
```

### URLs de Produção
- **Aplicação**: `http://localhost`
- **API Documentation**: `http://localhost/api/docs`
- **Health Check**: `http://localhost/api/health`
- **Grafana**: `http://localhost/grafana/` (admin/admin)
- **Prometheus**: `http://localhost/prometheus/`

### Considerações de Produção
- **Segurança**: Nginx como proxy reverso (porta 80 apenas)
- **Isolamento**: Serviços em rede interna Docker
- **Monitoramento**: Prometheus + Grafana + Loki habilitados por padrão

## 📝 Variáveis de Ambiente

### Required
- `OPENAI_API_KEY` - Chave da OpenAI
- `GOOGLE_API_KEY` - Chave do Google AI
- `GROQ_API_KEY` - Chave do Groq
- `DATABASE_URL` - String de conexão PostgreSQL
- `REDIS_URL` - String de conexão Redis

### Optional
- `CORS_ORIGINS` - Origens permitidas para CORS
- `SECRET_KEY` - Chave secreta para JWT

### Monitoramento
- `GRAFANA_ADMIN_USER` - Usuário admin do Grafana (padrão: admin)
- `GRAFANA_ADMIN_PASSWORD` - Senha do Grafana (padrão: admin)

## 🔧 Desenvolvimento

### Estrutura de Diretórios
```
apps/
├── web/                 # Frontend Next.js
│   ├── app/            # App Router pages
│   │   ├── (auth)/     # Rotas de autenticação
│   │   ├── (dashboard)/ # Rotas do dashboard
│   │   └── api/        # Rotas de API do Next.js
│   ├── components/     # Componentes React reutilizáveis
│   └── lib/           # Utilities e types
└── api/                # Backend FastAPI
    ├── app/           # Application code
    │   ├── api/       # API routes (v1)
    │   ├── core/      # Core modules (config, db, security, metrics, setup)
    │   ├── models/    # Database models
    │   ├── schemas/   # Pydantic schemas
    │   ├── services/  # Camada de serviços (AuthService, ChatService, etc.)
    │   └── utils/     # Business logic
    └── tests/         # Test suite
```

### Comandos Úteis
```bash
# Logs em tempo real
docker compose logs -f

# Rebuild específico
docker compose up --build web

# Limpar volumes
docker compose down -v
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma feature branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: support@seuprojeto.com
- 📖 Documentation: `/docs`
- 🐛 Issues: GitHub Issues

## 📜 CHANGELOG

Para um histórico detalhado de todas as alterações e refatorações, consulte o arquivo [`CHANGELOG.md`](CHANGELOG.md).

---

**Built with ❤️ using modern web technologies**
