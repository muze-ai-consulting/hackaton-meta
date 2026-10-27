---
description: Rules for Python files
globs: **/*.py
---

- Use type hints on all function signatures
- Use `logging` module, never bare `print()` for production output
- Use `asyncio` + `aiohttp` or `httpx` for async HTTP, not `requests` in async code
- Use f-strings, not `.format()` or `%`
- Handle exceptions specifically, never bare `except:`
- After editing: run `python -c "import ast; ast.parse(open('FILE').read())"` to verify syntax
