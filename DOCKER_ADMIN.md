# Como Definir Usuário Administrador via Docker

## Método 1: Acessar o Container do Banco de Dados

### 1. Encontrar o nome do container PostgreSQL
```bash
docker ps | grep postgres
```

### 2. Acessar o container do PostgreSQL
```bash
docker exec -it <nome-do-container-postgres> psql -U postgres -d <nome-do-banco>
```

### 3. Tornar usuário existente como admin
```sql
UPDATE "user" SET is_admin = true WHERE email = 'seu-email@exemplo.com';
```

### 4. Verificar se funcionou
```sql
SELECT email, is_admin, is_active FROM "user" WHERE email = 'seu-email@exemplo.com';
```

### 5. Sair do PostgreSQL
```sql
\q
```

## Método 2: Via Container da API (Python)

### 1. Acessar o container da API
```bash
docker exec -it <nome-do-container-api> bash
```

### 2. Usar Python para tornar admin
```bash
python -c "
from sqlmodel import Session, select, create_engine
from app.models.user import User
from app.core.db import DATABASE_URL

engine = create_engine(DATABASE_URL)
with Session(engine) as session:
    user = session.exec(select(User).where(User.email == 'seu-email@exemplo.com')).first()
    if user:
        user.is_admin = True
        session.commit()
        print(f'Usuário {user.email} agora é admin!')
    else:
        print('Usuário não encontrado')
"
```

## Método 3: Via Docker Compose (Mais Fácil)

### 1. Criar script SQL
Crie um arquivo `make_admin.sql`:
```sql
UPDATE "user" SET is_admin = true WHERE email = 'seu-email@exemplo.com';
```

### 2. Executar o script no container
```bash
docker compose exec postgres psql -U postgres -d <nome-do-banco> -f /path/to/make_admin.sql
```

## Método 4: Via API REST (Recomendado)

### 1. Registrar novo usuário (se não tiver)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@seusistema.com",
    "password": "senha_forte123",
    "full_name": "Administrador do Sistema"
  }'
```

### 2. Acessar o banco e tornar admin
```bash
docker compose exec postgres psql -U postgres -d <nome-do-banco> -c "
UPDATE \"user\" SET is_admin = true WHERE email = 'admin@seusistema.com';
"
```

## Informações do Container

### Nomes padrão (verifique com `docker ps`):
- **PostgreSQL**: `saas-chatbot-ai-docker-prod-postgres-1`
- **API**: `saas-chatbot-ai-docker-prod-api-1`

### Database name:
- Geralmente: `postgres` ou verifique no `.env`

## Exemplo Completo

```bash
# 1. Ver containers
docker ps

# 2. Acessar PostgreSQL (substitua nomes)
docker exec -it saas-chatbot-ai-docker-prod-postgres-1 psql -U postgres -d postgres

# 3. Tornar admin
UPDATE "user" SET is_admin = true WHERE email = 'seu-email@exemplo.com';

# 4. Verificar
SELECT email, is_admin FROM "user" WHERE email = 'seu-email@exemplo.com';

# 5. Sair
\q

# 6. Fazer login no sistema
# Acesse: http://localhost:3000
# Use seu email/senha
# Botão "Admin" aparecerá no header
```

## Verificação Final

Após os passos:
1. Faça login com o usuário modificado
2. Você deve ver o botão **"Admin"** no header (roxo)
3. Clique para acessar o painel administrativo
4. Você poderá gerenciar todos os usuários

## Segurança

⚠️ **Importante**:
- Use senhas fortes para usuários admin
- Considere remover o acesso direto ao banco em produção
- Monitore logs de atividades admin
- Crie usuários admin separados do seu usuário normal
