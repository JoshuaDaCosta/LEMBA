# Boas praticas de seguranca para desenvolvimento Django

## Configuracao e segredos
- Nunca guardes `SECRET_KEY`, palavras-passe, tokens ou credenciais no codigo fonte.
- Usa variaveis de ambiente para dados sensiveis e mantem um ficheiro `.env.example` sem segredos reais.
- Mantem `DEBUG=False` em producao.
- Define `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `SECURE_PROXY_SSL_HEADER` correctamente antes de publicar.

## Dependencias
- Instala apenas bibliotecas necessarias.
- Mantem dependencias actualizadas e revê vulnerabilidades regularmente.
- Usa o teu `requirements.txt` como fonte controlada de versoes.

## Django settings
- Activa `SecurityMiddleware`.
- Em producao usa `SESSION_COOKIE_SECURE=True` e `CSRF_COOKIE_SECURE=True`.
- Activa `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = 'DENY'` ou politica equivalente.
- Redirecciona HTTP para HTTPS com `SECURE_SSL_REDIRECT=True` quando aplicavel.

## Base de dados
- Usa utilizadores com privilegios minimos.
- Nunca montes queries SQL com concatenacao de strings; prefere ORM ou queries parametrizadas.
- Faz migracoes com controlo e backups antes de alteracoes sensiveis.

## Autenticacao e autorizacao
- Valida autenticacao e permissoes em todas as views sensiveis.
- Usa `@login_required`, classes de permissao e verificacoes de ownership quando necessario.
- Nunca assumes que esconder elementos no frontend protege recursos.
- Considera MFA para contas administrativas.

## Validacao de entrada
- Valida e saneia toda a entrada do utilizador com forms, serializers e validadores.
- Limita upload de ficheiros por tipo, tamanho e extensao.
- Escapa output dinamico e evita `mark_safe` excepto quando for estritamente necessario e auditado.

## Templates e frontend
- Mantem autoescape activo.
- Protege formularios com `{% csrf_token %}`.
- Nao exponhas dados internos, stacks ou configuracoes em mensagens de erro.

## Logs e monitorizacao
- Regista erros e eventos relevantes sem gravar passwords, tokens ou dados pessoais sensiveis.
- Configura alertas para falhas repetidas de login, erros 500 e actividades anormais.

## Processo de desenvolvimento
- Revê codigo antes de publicar.
- Cria testes para autenticacao, autorizacao e validacoes criticas.
- Separa ambientes de desenvolvimento, teste e producao.
- Aplica o principio do menor privilegio em ficheiros, serviços e acessos.
