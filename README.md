# NGINX Wiki

Community documentation for **NGINX configuration, architecture, and module development**.

🌐 **Live site:** [nginx-wiki.getpagespeed.com](https://nginx-wiki.getpagespeed.com/)

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## 🚀 Quick Start

```bash
# Create an isolated environment and install dependencies
uv venv .venv
uv pip install --python .venv/bin/python --requirement requirements.txt

# Start dev server (http://127.0.0.1:9898)
.venv/bin/mkdocs serve -a 127.0.0.1:9898

# Build and verify the static site
make test
```

## 📁 Structure

```
docs/
├── architecture/     # Process model, event loop, request lifecycle
├── core-apis/        # C API reference (ngx_http_*, memory, logging)
├── modules-dev/      # Module development guides
├── config/           # Configuration examples & recipes
│   ├── examples/     # Load balancing, SSL, FastCGI, etc.
│   ├── recipes/      # WordPress, Django, Ruby, etc.
│   └── platforms/    # Solaris, OpenBSD, etc.
├── ecosystem/        # 3rd-party modules catalog
└── community/        # FAQ, IRC, contributing
```

## 🐳 Docker

```bash
docker-compose up --build
# Browse to http://localhost:8000
```

## 🌍 Translations

The site supports multiple languages via `mkdocs-static-i18n`. Currently:
- **English** (default)
- **Russian** (in progress)

To add translations, create files with `.ru.md` suffix.

## 📄 License

This documentation is community-maintained. NGINX is a registered trademark of F5, Inc.
