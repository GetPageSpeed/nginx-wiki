---
title: Examples
---

# Configuration Examples

The original NGINX Wiki contained many **configuration examples and application-specific recipes**. This section curates and modernizes those examples.

---

## Full Configurations

| Example | Description |
|---------|-------------|
| [Full example](full.md) | A complete multi-server configuration with FastCGI, reverse proxy, and load balancing |
| [Another full example](full-2.md) | Alternative configuration covering proxying, rewriting, and static files |

---

## Load Balancing & Proxying

| Example | Description |
|---------|-------------|
| [Simple load balancing](load-balancing.md) | Basic upstream load balancing with weighted servers |
| [Reverse proxy with caching](reverse-proxy-caching.md) | Caching proxy configuration |
| [SSL/TLS termination](ssl-termination.md) | HTTPS offloading and HTTP-to-HTTPS redirect |
| [X-Accel (X-Sendfile)](x-accel.md) | Internal redirects for protected file downloads |
| [Forwarded header](forwarded-header.md) | RFC 7239 standardized proxy headers |

---

## Server Configuration

| Example | Description |
|---------|-------------|
| [Server blocks](server-blocks.md) | Virtual hosts, wildcards, and default servers |
| [FastCGI setup](fastcgi.md) | Spawning processes and securing uploads |

---

## Operations

| Example | Description |
|---------|-------------|
| [Systemd service](systemd.md) | Modern service management |
| [Init scripts](init-scripts.md) | SysVinit, Upstart, FreeBSD rc.d, macOS launchd |
| [Log rotation](log-rotation.md) | Rotating logs with USR1 signal |

---

## Application Recipes

For application-specific configurations (WordPress, Drupal, Symfony, etc.), see the [Application Recipes](../recipes/index.md) section.
