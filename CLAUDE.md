# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NGINX Wiki - community documentation for NGINX configuration, architecture, and module development. Built with MkDocs Material.

Live site: https://nginx-wiki.getpagespeed.com/

## Commands

```bash
# Install dependencies
uv venv .venv
uv pip install --python .venv/bin/python --requirement requirements.txt

# Start dev server (http://127.0.0.1:9898)
.venv/bin/mkdocs serve -a 127.0.0.1:9898

# Build static site to site/
make test

# Docker alternative (http://localhost:8000)
docker-compose up --build
```

## Documentation Structure

All documentation lives in `docs/` as Markdown files:

- `architecture/` - NGINX internals: process model, event loop, request lifecycle
- `core-apis/` - C API reference (ngx_http_*, memory, logging, etc.)
- `modules-dev/` - Module development guides and compilation
- `config/` - Configuration guides, examples, recipes, and platform-specific guides
- `ecosystem/` - 3rd-party modules catalog
- `community/` - FAQ, IRC, contributing guidelines

Navigation structure is defined in `mkdocs.yml` under `nav:`.

## Translations

Uses `mkdocs-static-i18n` plugin. To add Russian translations, create files with `.ru.md` suffix (e.g., `index.ru.md` alongside `index.md`).
