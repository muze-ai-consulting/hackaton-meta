---
description: Never expose secrets in code or commits
globs: "**/.env,**/*.pem,**/*credentials*,**/*secret*"
---

- NEVER read, display, or include secrets in responses
- NEVER commit .env files or .pem keys
- Use environment variables for all secrets
- If a secret is needed in Docker: use docker-compose env_file, never COPY .env
- If a secret appears in logs or output: warn Mark immediately
