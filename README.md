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
docker compose up --build

# Acesse os serviços
# Frontend: http://localhost:3000/register
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
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
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │      API        │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ - UI/UX         │    │ - Business      │    │ - Conversations │
│ - State Mgmt    │    │   Logic         │    │ - Messages      │
│ - AI SDK        │    │ - Validation    │    │ - Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Cache)       │
                    │                 │
                    │ - Sessions      │
                    │ - Rate Limiting │
                    └─────────────────┘
```

## 🚀 Deploy em Produção

### Configuração de Produção
```bash
# Configure para produção
cp .env.prod.example .env
# Ajuste variáveis de ambiente

# Suba em modo produção
docker compose -f docker-compose.prod.yml up --build -d
```

### URLs de Produção
- **Aplicação**: `http://localhost`
- **API Documentation**: `http://localhost/api/docs`
- **Health Check**: `http://localhost/api/health`

### Considerações de Produção
- **Segurança**: Nginx como proxy reverso (porta 80 apenas)
- **Isolamento**: Serviços em rede interna Docker
- **Próximos Passos**:
  - Configurar HTTPS (Cloudflare/Let's Encrypt)
  - Implementar backups automáticos do PostgreSQL
  - Configurar migrações com Alembic
  - Monitoramento e logging centralizado

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

## 🔧 Desenvolvimento

### Estrutura de Diretórios
```
apps/
├── web/                 # Frontend Next.js
│   ├── app/            # App Router pages
│   ├── components/     # Reusable components
│   └── lib/           # Utilities e types
└── api/                # Backend FastAPI
    ├── app/           # Application code
    │   ├── api/       # API routes
    │   ├── models/    # Database models
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

---

**Built with ❤️ using modern web technologies**
