# Script para atualizar tabela User com campos admin

## Execute no container PostgreSQL:

docker exec -it d7f9e7016b77 psql -U saas_chat -d saas_chat

## Comandos SQL:

-- 1. Adicionar coluna is_admin
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- 2. Adicionar coluna full_name 
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS full_name VARCHAR(120);

-- 3. Adicionar coluna last_login
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- 4. Remover coluna name (se existir)
ALTER TABLE "user" DROP COLUMN IF EXISTS name;

-- 5. Tornar seu usuário admin
UPDATE "user" SET is_admin = true WHERE email = 'diego.veras@gmail.com';

-- 6. Verificar resultado
SELECT email, full_name, is_admin, is_active, created_at FROM "user" WHERE email = 'diego.veras@gmail.com';

## Execute tudo de uma vez:

COPY AND PASTE:
```
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS full_name VARCHAR(120);
ALTER TABLE "user" DROP COLUMN IF EXISTS name;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
UPDATE "user" SET is_admin = true WHERE email = 'diego.veras@gmail.com';
SELECT email, is_admin, is_active FROM "user" WHERE email = 'diego.veras@gmail.com';
```

## Saia do PostgreSQL:
\q
