# SaaS Chatbot AI - Docker

Projeto base com:
- Next.js 15 + App Router
- Vercel AI SDK
- OpenAI / Gemini / Groq / Together via provider dinâmico
- FastAPI + SQLModel
- PostgreSQL
- Redis
- Docker Compose

## Como subir

1. Preencha as chaves no arquivo `.env` na raiz.
2. Rode:

```bash
docker compose up --build
```

3. Acesse:
- Frontend: http://localhost:3000/register
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Fluxo de teste

1. Abra `/register`
2. Crie a conta
3. Você será enviado ao dashboard
4. Escolha o provider
5. Envie mensagens

## Observações

- O banco é criado automaticamente via `SQLModel.metadata.create_all`.
- Em produção, substitua isso por migrações com Alembic.
- O histórico de mensagens salva `provider` e `model`.
- O projeto usa volumes bind para hot reload no desenvolvimento.


## Produção com Docker

Arquivos adicionados:
- `docker-compose.prod.yml`
- `apps/web/Dockerfile`
- `apps/api/Dockerfile`
- `infra/nginx/default.conf`
- `.env.prod.example`

### Como subir em modo produção local

1. Copie `.env.prod.example` para `.env`
2. Ajuste as chaves e segredos
3. Rode:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

4. Acesse:
- Aplicação: `http://localhost`
- API docs: `http://localhost/api/docs`
- Health: `http://localhost/api/health`

### Observações de produção

- O Nginx publica apenas a porta 80.
- `web`, `api`, `db` e `redis` ficam apenas na rede interna do Compose.
- Para um VPS real, o próximo passo recomendado é adicionar HTTPS no proxy reverso, backups do PostgreSQL e migrações com Alembic.
- Se você usar Cloudflare, mantenha o `CORS_ORIGINS` coerente com o domínio final.
