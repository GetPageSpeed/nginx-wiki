---
title: NGINX Simple Load Balancing Configuration Example
description: Learn how to configure NGINX load balancing with upstream servers, weighted distribution, and round-robin algorithms for high availability.
keywords: nginx load balancing, nginx upstream, nginx weight, nginx round robin, nginx high availability, nginx backend
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - load balancing
  - upstream
  - high availability
  - round robin
---

# Simple Load Balancing

An example NGINX configuration that performs simple load balancing across multiple backend servers.

## nginx.conf

```nginx
http {
  upstream myproject {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;    
    server 127.0.0.1:8003;
  }

  server {
    listen 80;
    server_name www.domain.com;
    location / {
      proxy_pass http://myproject;
    }
  }
}
```

## Key points

- The `upstream` block defines a group of backend servers.
- The `weight` parameter controls load distribution (higher weight = more requests).
- By default, NGINX uses round-robin load balancing.
- Other load balancing methods include `least_conn`, `ip_hash`, and `hash`.


