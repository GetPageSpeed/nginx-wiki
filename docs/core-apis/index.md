---
title: NGINX Core C APIs Reference - Module Development API Documentation
description: Complete reference for NGINX's internal C APIs. Master ngx_http_request_t, ngx_module_t, memory pools, buffers, logging, and configuration helpers for building powerful NGINX modules.
keywords: nginx c api, nginx module api, ngx_http_request_t, ngx_module_t, nginx memory pool, nginx development, nginx internals, nginx c programming, nginx module development
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - api
  - c-programming
  - module-development
  - reference
---

# Core C APIs

The **core NGINX C APIs** expose the internal types, structures, and functions that modules use to:

- Integrate with the master/worker process model
- Hook into the HTTP / mail / stream subsystems
- Allocate memory, log events, and schedule timers

This section is based on the historical *Module API* documentation from the original NGINX Wiki, restructured as Markdown for MkDocs.

It is organised as:

- [Module API](module-api.md): high-level overview and table of contents
- [Main module API](main-module-api.md): types and structures in the ``main`` module context
- [Event handling API](event-api.md): working with the event loop
- [HTTP API](http-api.md): HTTP-specific types, headers, requests, responses, and helpers
- [Mail API](mail-api.md): mail subsystem structures and hooks



