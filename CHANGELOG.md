# CHANGELOG

Este documento registra todas as alterações significativas, refatorações e correções implementadas no projeto SaaS Chatbot AI.

## Versão 1.0.0 (2026-04-12)

### Novas Funcionalidades

*   **Monitoramento Robusto com Promtail**: Implementado Promtail para coleta de logs de todos os contêineres Docker, substituindo o driver de log do Docker. Isso garante maior resiliência e desacoplamento na coleta de logs para o Loki.

### Refatorações

*   **API de Backend (`apps/api`) - Baixo Acoplamento**:
    *   Introdução de uma **camada de serviços** (`apps/api/app/services/`) para encapsular a lógica de negócios de autenticação, chats, workspaces e administração.
        *   `AuthService`: Gerencia a lógica de registro, login e verificação de usuários.
        *   `ChatService`: Gerencia a lógica de listagem, criação, exclusão de conversas e mensagens.
        *   `WorkspaceService`: Gerencia a lógica de listagem de workspaces.
        *   `AdminService`: Gerencia a lógica de estatísticas administrativas, listagem, criação e atualização de usuários.
    *   **`apps/api/app/main.py`**: Simplificado, movendo a configuração das métricas Prometheus para `apps/api/app/core/metrics_setup.py` e a inicialização do banco de dados para `apps/api/app/core/database_setup.py`.
    *   **Roteadores da API (`apps/api/app/api/v1/`)**: Refatorados para serem mais "magros", delegando a lógica de negócios para os respectivos serviços.

### Correções de Bugs

*   **Loki - Permissões de Escrita**: Corrigido problema de permissão de escrita no Loki (`mkdir /tmp/loki/rules: permission denied`) ao executar o serviço Loki como `user: root` no `docker-compose.prod.yml`.
*   **Grafana - Datasources Não Encontrados**: Resolvido o erro `Failed to build rule evaluator" error="failed to build query 'A': data source not found"` adicionando `uid`s estáticos às fontes de dados em `infra/grafana/datasources/datasources.yml`.
*   **Grafana - Sintaxe de Alerta**: Atualizada a sintaxe das regras de alerta em `infra/grafana/alerting/alert-rules.yml` para o formato `conditions` mais recente, corrigindo `threshold expression requires exactly one condition`.
*   **Grafana - Redirecionamento Infinito**: Corrigido o problema de `ERR_TOO_MANY_REDIRECTS` ao acessar o Grafana, ajustando a configuração de `proxy_pass` no Nginx (`infra/nginx/default.conf`) e garantindo a consistência do `GF_SERVER_ROOT_URL` no `docker-compose.prod.yml`.
*   **Grafana - WebSockets para Live**: Adicionado suporte a WebSockets na configuração do Nginx para o Grafana (`infra/nginx/default.conf`), resolvendo erros HTTP 400 em funcionalidades "Live".
*   **Redis Exporter - Healthcheck**: Removido o healthcheck do `redis-exporter` em `docker-compose.prod.yml`, pois dependia de `wget` que não estava presente na imagem.

### Removido

*   **`setup-monitoring.bat`**: Arquivo removido, pois sua funcionalidade (instalação do driver de log do Docker) tornou-se obsoleta com a adoção do Promtail.
