---
title: NGINX Configuration, Architecture & Module Development
description: The community-maintained NGINX reference for configuration patterns, event-driven architecture, C APIs, and custom module development.
keywords: nginx wiki, nginx documentation, nginx configuration, nginx tutorial, nginx guide, web server, reverse proxy, load balancer, nginx modules, nginx development, nginx architecture, nginx c api, high performance web server
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: WebSite
og_type: website
hide:
  - navigation
  - toc
tags:
  - nginx
  - documentation
  - web server
  - configuration
---

<div class="hero" markdown="1">

# NGINX Wiki

The **definitive community resource** for NGINX internals, configuration patterns, and module development.

Understand how NGINX really works: the event-driven architecture, master/worker process model, C APIs, and how your configuration maps onto those internals.

<div class="hero-actions" markdown="1">

[Get Started](architecture/index.md){ .md-button .md-button--primary }
[Browse APIs](core-apis/index.md){ .md-button }
[View Recipes](config/recipes/index.md){ .md-button }

</div>

<div class="hero-stats" markdown="1">

<div class="hero-stat">
<div class="hero-stat-value">100+</div>
<div class="hero-stat-label">Config Recipes</div>
</div>

<div class="hero-stat">
<div class="hero-stat-value">50+</div>
<div class="hero-stat-label">API References</div>
</div>

<div class="hero-stat">
<div class="hero-stat-value">Open</div>
<div class="hero-stat-label">Source</div>
</div>

</div>

</div>

<div class="terminal-demo">
<div class="terminal-header">
<div class="terminal-dots">
<span class="terminal-dot red"></span>
<span class="terminal-dot yellow"></span>
<span class="terminal-dot green"></span>
</div>
<div class="terminal-title">nginx.conf — Example Configuration</div>
</div>
<div class="terminal-body">
<div class="terminal-line">
<span class="terminal-command" style="color: var(--accent-purple);">http</span> <span style="color: var(--text-muted);">{</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="color: var(--accent-purple);">upstream</span> <span style="color: var(--accent-cyan);">backend</span> <span style="color: var(--text-muted);">{</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--nginx-green);">server</span> <span style="color: var(--text-secondary);">127.0.0.1:8080 weight=5;</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--nginx-green);">server</span> <span style="color: var(--text-secondary);">127.0.0.1:8081 backup;</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="color: var(--text-muted);">}</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="color: var(--accent-purple);">server</span> <span style="color: var(--text-muted);">{</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--nginx-green);">listen</span> <span style="color: var(--accent-orange);">443</span> <span style="color: var(--accent-cyan);">ssl http2</span>;
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--nginx-green);">server_name</span> <span style="color: var(--text-secondary);">example.com;</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--accent-purple);">location</span> <span style="color: var(--accent-cyan);">/</span> <span style="color: var(--text-muted);">{</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 4.5rem; color: var(--nginx-green);">proxy_pass</span> <span style="color: var(--text-secondary);">http://backend;</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="padding-left: 3rem; color: var(--text-muted);">}</span>
</div>
<div class="terminal-line">
<span class="terminal-output" style="color: var(--text-muted);">}</span>
</div>
<div class="terminal-line">
<span style="color: var(--text-muted);">}</span>
</div>
</div>
</div>

## Explore the Documentation

<div class="feature-grid" markdown="1">

<div class="feature-card" markdown="1">

### :material-cpu-64-bit: Architecture Deep Dive

Master NGINX internals: the **master/worker** process model, non-blocking I/O, event loop mechanics, timers, and the complete HTTP request lifecycle.

[Explore Architecture](architecture/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-code-braces: Core C APIs

Complete reference for `ngx_http_request_t`, `ngx_module_t`, memory pools, buffer chains, logging subsystems, and configuration parsing.

[Browse API Reference](core-apis/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-puzzle: Module Development

Build custom handlers, filters, and load balancers. Learn compilation workflows, configuration structures, and debug techniques.

[Start Building](modules-dev/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-chef-hat: Configuration Recipes

Production-ready configs for **WordPress, Laravel, Django, Ruby**, and 50+ frameworks. Copy, paste, and customize.

[View All Recipes](config/recipes/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-shield-lock: Security & SSL

TLS best practices, certificate management, HTTP/2 and HTTP/3 setup, security headers, and hardening guides.

[Security Guide](config/security.md)

</div>

<div class="feature-card" markdown="1">

### :material-scale-balance: Load Balancing

Upstream configuration, health checks, session persistence, weighted distribution, and failover strategies.

[Load Balancing](config/load-balancing.md)

</div>

</div>

## Quick Links

<div class="feature-grid" markdown="1">

<div class="feature-card" markdown="1">

### :material-rocket-launch: Getting Started

New to NGINX? Start here with installation, basic configuration, and your first reverse proxy setup.

[Quick Start Guide](config/getting-started.md)

</div>

<div class="feature-card" markdown="1">

### :material-alert-circle: Common Pitfalls

Avoid the most frequent configuration mistakes. Learn why "if is evil" and other gotchas that trip up newcomers.

[Read Pitfalls](config/pitfalls.md)

</div>

</div>

---

<div style="text-align: center; padding: 2rem 0; color: var(--text-muted);">

**NGINX Wiki** is a community-driven project.
[Contribute on GitHub](https://github.com/GetPageSpeed/nginx-wiki){ .md-button } &nbsp; [Join the Community](community/get-involved.md){ .md-button }

</div>
