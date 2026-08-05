---
title: NGINX Reverse Proxy with Caching Configuration
description: Configure NGINX as a caching reverse proxy with proxy_cache_path, cache zones, stale content serving, and cache validation settings.
keywords: nginx reverse proxy, nginx caching, proxy_cache, nginx cache zone, nginx stale cache, nginx proxy_cache_valid
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - reverse proxy
  - caching
  - proxy cache
  - performance
---

# Reverse Proxy with Caching

An example NGINX configuration that acts as a reverse proxy with caching enabled.

## nginx.conf

```nginx
http {
    proxy_cache_path  /data/nginx/cache  levels=1:2    keys_zone=STATIC:10m
    inactive=24h  max_size=1g;

    server {
        location / {
            proxy_pass             http://1.2.3.4;
            proxy_set_header       Host $host;
            proxy_buffering        on;
            proxy_cache            STATIC;
            proxy_cache_valid      200  1d;
            proxy_cache_use_stale  error timeout invalid_header updating
                                   http_500 http_502 http_503 http_504;
        }
    }
}
```

## Key points

- `proxy_cache_path` defines the cache location, structure, and limits.
- `levels=1:2` creates a two-level directory hierarchy for cache files.
- `keys_zone=STATIC:10m` allocates 10 MB of shared memory for cache keys.
- `inactive=24h` removes cached items not accessed within 24 hours.
- `proxy_cache_valid` sets how long responses with specific status codes are cached.
- `proxy_cache_use_stale` serves stale content when the backend is unavailable.


