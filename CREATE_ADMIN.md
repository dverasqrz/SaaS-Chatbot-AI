# Criar Usuário Admin Inicial

## Método 1: Via API REST

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@exemplo.com",
    "password": "senha123",
    "full_name": "Administrador"
  }'
```

## Método 2: Via Interface Web

1. Acesse: http://localhost:3000/register
2. Preencha:
   - Email: admin@exemplo.com
   - Senha: senha123
   - Nome: Administrador
3. Clique em registrar

## Método 3: Via Database (Se necessário)

Se precisar criar diretamente no banco:

```sql
INSERT INTO "user" (id, email, full_name, password_hash, is_admin, is_active, created_at)
VALUES (
  'admin-id-uuid',
  'admin@exemplo.com',
  'Administrador',
  'hash-da-senha',
  true,
  true,
  NOW()
);
```

## Tornar Usuário Existente como Admin

Se você já tem um usuário e quer torná-lo admin:

```sql
UPDATE "user" SET is_admin = true WHERE email = 'seu-email@exemplo.com';
```

## Acesso Após Criação

1. Faça login com: admin@exemplo.com / senha123
2. Você verá o botão "Admin" no header
3. Acesse o painel em: http://localhost:3000/admin

## Segurança

⚠️ **Importante**: Em produção, altere a senha padrão imediatamente após o primeiro acesso!

- Use senhas fortes
- Habilite autenticação de dois fatores (se implementado)
- Limpe usuários de teste após configuração
