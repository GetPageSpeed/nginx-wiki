---
title: NGINX Load Balancing - Upstream Configuration & High Availability Guide
description: Configure NGINX load balancing with upstream servers. Learn round-robin, least connections, IP hash, weighted distribution, health checks, and failover strategies for high availability.
keywords: nginx load balancing, nginx upstream, nginx round robin, nginx least connections, nginx ip hash, nginx health check, nginx failover, nginx high availability, nginx reverse proxy
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - load-balancing
  - upstream
  - high-availability
  - reverse-proxy
---

# Load Balancing

NGINX can distribute traffic across multiple backend servers for high availability and scalability.

---

## Basic Load Balancing

### Round Robin (Default)

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Load Balancing Methods

### Least Connections

Send to server with fewest active connections:

```nginx
upstream backend {
    least_conn;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}
```

### IP Hash (Session Persistence)

Same client always goes to same server:

```nginx
upstream backend {
    ip_hash;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}
```

### Generic Hash

Hash on custom key:

```nginx
upstream backend {
    hash $request_uri consistent;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}
```

### Random with Two Choices

```nginx
upstream backend {
    random two least_conn;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}
```

---

## Server Parameters

```nginx
upstream backend {
    server 10.0.0.1:8080 weight=5;           # 5x more traffic
    server 10.0.0.2:8080 weight=3;           # 3x more traffic
    server 10.0.0.3:8080;                    # weight=1 (default)
    server 10.0.0.4:8080 backup;             # Only used when others fail
    server 10.0.0.5:8080 down;               # Marked as unavailable
    server 10.0.0.6:8080 max_fails=3 fail_timeout=30s;
    server 10.0.0.7:8080 max_conns=100;      # Limit connections
}
```

| Parameter | Description |
|-----------|-------------|
| `weight=N` | Server weight for load balancing |
| `max_fails=N` | Failures before marking unavailable |
| `fail_timeout=N` | Time to consider server unavailable |
| `backup` | Only use when primary servers unavailable |
| `down` | Mark server as permanently unavailable |
| `max_conns=N` | Max concurrent connections |

---

## Health Checks

### Passive Health Checks

Built into NGINX (free):

```nginx
upstream backend {
    server 10.0.0.1:8080 max_fails=3 fail_timeout=30s;
    server 10.0.0.2:8080 max_fails=3 fail_timeout=30s;
}
```

### Active Health Checks (NGINX Plus)

```nginx
upstream backend {
    zone backend 64k;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;

    # Active health check
    health_check interval=5s fails=3 passes=2;
}

location / {
    proxy_pass http://backend;
}

# Health check location
location @health_check {
    internal;
    proxy_pass http://backend/health;
}
```

### Custom Health Check with Lua

Using OpenResty/lua-nginx-module:

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

# Use lua-resty-upstream-healthcheck module
init_worker_by_lua_block {
    local hc = require "resty.upstream.healthcheck"
    local ok, err = hc.spawn_checker{
        shm = "healthcheck",
        upstream = "backend",
        type = "http",
        http_req = "GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n",
        interval = 2000,
        timeout = 1000,
        fall = 3,
        rise = 2,
    }
}
```

---

## Session Persistence

### Cookie-Based (Sticky Sessions)

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;

    # Sticky cookie (NGINX Plus feature)
    # sticky cookie srv_id expires=1h domain=.example.com path=/;
}

# Alternative with map (free NGINX)
map $cookie_backend_server $backend_sticky {
    default backend;
    server1 10.0.0.1:8080;
    server2 10.0.0.2:8080;
}

server {
    location / {
        proxy_pass http://$backend_sticky;
        add_header Set-Cookie "backend_server=server1; Path=/; HttpOnly";
    }
}
```

### Route-Based

```nginx
map $request_uri $backend {
    ~^/api/users     api_users;
    ~^/api/products  api_products;
    default          api_default;
}

upstream api_users {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

upstream api_products {
    server 10.0.0.3:8080;
    server 10.0.0.4:8080;
}

upstream api_default {
    server 10.0.0.5:8080;
}

server {
    location /api {
        proxy_pass http://$backend;
    }
}
```

---

## Connection Pooling

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;

    keepalive 32;              # Keep 32 connections open
    keepalive_requests 1000;   # Max requests per connection
    keepalive_timeout 60s;     # Idle timeout
}

server {
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

---

## SSL/TLS Backends

### HTTPS to Backend

```nginx
upstream backend_ssl {
    server 10.0.0.1:443;
    server 10.0.0.2:443;
}

server {
    location / {
        proxy_pass https://backend_ssl;
        proxy_ssl_verify on;
        proxy_ssl_trusted_certificate /etc/nginx/ssl/ca.crt;
        proxy_ssl_server_name on;
    }
}
```

### SSL Termination at NGINX

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

server {
    listen 443 ssl;
    http2 on;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    location / {
        proxy_pass http://backend;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Failover and High Availability

### Primary/Backup

```nginx
upstream backend {
    server 10.0.0.1:8080;           # Primary
    server 10.0.0.2:8080;           # Primary
    server 10.0.0.3:8080 backup;    # Backup
}
```

### Slow Start

Gradually increase traffic to recovered server:

```nginx
upstream backend {
    server 10.0.0.1:8080 slow_start=30s;
    server 10.0.0.2:8080 slow_start=30s;
}
```

### Queue Requests

Queue requests when all servers are busy:

```nginx
upstream backend {
    server 10.0.0.1:8080 max_conns=100;
    server 10.0.0.2:8080 max_conns=100;
    queue 100 timeout=30s;
}
```

---

## Monitoring

### Upstream Status

```nginx
server {
    location /upstream_status {
        allow 127.0.0.1;
        deny all;
        stub_status;
    }
}
```

### Detailed Status (NGINX Plus)

```nginx
server {
    location /api {
        api write=on;
        allow 127.0.0.1;
        deny all;
    }

    location = /dashboard.html {
        root /usr/share/nginx/html;
    }
}
```

---

## Layer 4 (TCP/UDP) Load Balancing

```nginx
stream {
    upstream database {
        server 10.0.0.1:3306 weight=5;
        server 10.0.0.2:3306;
        server 10.0.0.3:3306 backup;
    }

    server {
        listen 3306;
        proxy_pass database;
        proxy_connect_timeout 1s;
    }
}
```

### UDP Load Balancing

```nginx
stream {
    upstream dns {
        server 10.0.0.1:53;
        server 10.0.0.2:53;
    }

    server {
        listen 53 udp;
        proxy_pass dns;
        proxy_responses 1;
    }
}
```

---

## Common Patterns

### Blue-Green Deployment

```nginx
upstream blue {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

upstream green {
    server 10.0.0.3:8080;
    server 10.0.0.4:8080;
}

# Switch by changing this
map $host $deployment {
    default blue;
    # default green;  # Uncomment to switch
}

server {
    location / {
        proxy_pass http://$deployment;
    }
}
```

### Canary Deployment

```nginx
split_clients $request_id $backend {
    10%  canary;
    *    stable;
}

upstream stable {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

upstream canary {
    server 10.0.0.3:8080;
}

server {
    location / {
        proxy_pass http://$backend;
    }
}
```

---

## See Also

- [Security Hardening](security.md)
- [SSL/TLS Configuration](ssl.md)
- [HTTP/3 Configuration](http3.md)

