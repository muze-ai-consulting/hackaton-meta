---
description: Rules for Dockerfiles and docker-compose
globs: "**/Dockerfile,**/docker-compose*.yml"
---

- Use multi-stage builds to minimize image size
- Pin base image versions (e.g., `python:3.11-slim`, not `python:latest`)
- Use `.dockerignore` to exclude `.git`, `target/`, `node_modules/`, `.env`
- Expose ports explicitly and document them
- Use health checks in docker-compose
- For VPS deploys: always use docker-compose with restart: unless-stopped
