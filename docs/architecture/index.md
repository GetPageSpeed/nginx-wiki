---
title: NGINX Architecture Overview - Master/Worker Process Model & Event Loop
description: Deep dive into NGINX's high-performance architecture. Learn about the master/worker process model, event-driven non-blocking I/O, epoll/kqueue event loop, and modular design that handles 100,000+ requests per second.
keywords: nginx architecture, nginx process model, nginx event loop, nginx internals, nginx master worker, epoll kqueue, non-blocking io, nginx performance, event-driven web server, nginx design
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - architecture
  - internals
  - performance
  - event-driven
---

# Architecture Overview

NGINX is a high-performance, event-driven web server and reverse proxy. Understanding its architecture is essential for effective configuration and module development.

---

## Core Design Principles

### 1. Event-Driven, Non-Blocking

NGINX uses an **asynchronous, event-driven** model rather than threads:

- Single thread handles thousands of connections
- Non-blocking I/O for all operations
- Minimal memory overhead per connection (~256 bytes)

### 2. Master/Worker Process Model

```
┌─────────────────────────────────────────────────────────┐
│                      Master Process                      │
│  • Reads configuration          • Manages workers       │
│  • Binds privileged ports       • Handles signals       │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ Worker  │       │ Worker  │       │ Worker  │
   │    1    │       │    2    │       │    N    │
   └─────────┘       └─────────┘       └─────────┘
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
                    Event Loop
                 (epoll/kqueue)
```

### 3. Modular Architecture

Everything in NGINX is a module:

- **Core modules**: events, http, stream, mail
- **HTTP modules**: proxy, fastcgi, gzip, ssl, rewrite
- **Filter modules**: headers, gzip, ssi, charset

---

## Key Sections

| Section | Description |
|---------|-------------|
| [Process Model](process-model.md) | Master/worker architecture, signals, graceful reload |
| [Event Loop](event-loop.md) | epoll/kqueue, non-blocking I/O, timers |
| [Request Lifecycle](request-lifecycle.md) | HTTP phases, handlers, filters |

---

## Quick Facts

| Metric | Value |
|--------|-------|
| Connections per worker | 10,000+ typical |
| Memory per connection | ~256 bytes |
| Request throughput | 100,000+ req/sec |
| Context switches | Minimal (single-threaded) |

---

## Learning Path

1. **[Process Model](process-model.md)** - How NGINX manages processes
2. **[Event Loop](event-loop.md)** - The heart of NGINX performance
3. **[Request Lifecycle](request-lifecycle.md)** - How requests flow through phases
4. **[Core APIs](../core-apis/index.md)** - C structures and functions

---

## Further Reading

- [NGINX Development Guide](https://nginx.org/en/docs/dev/development_guide.html)
- [Inside NGINX](https://www.nginx.com/blog/inside-nginx-how-we-designed-for-performance-scale/)
- [The Architecture of Open Source Applications: NGINX](http://aosabook.org/en/nginx.html)
