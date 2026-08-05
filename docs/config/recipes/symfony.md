---
title: NGINX Symfony Configuration Guide
description: Production-ready NGINX configuration for Symfony 5, 6, and 7 with Webpack Encore, API Platform support, and FastCGI caching.
keywords: nginx, symfony, php framework, webpack encore, api platform, fastcgi, opcache preloading, deployment
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - symfony
  - php
  - api platform
  - webpack encore
  - deployment
---

# Symfony

Production-ready NGINX configuration for Symfony applications with security hardening and performance optimization.

---

## Symfony 6/7 (Recommended)

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com www.example.com;

    root /var/www/project/public;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/symfony.access.log;
    error_log /var/log/nginx/symfony.error.log;

    # Block access to hidden files
    location ~ /\. { deny all; }

    # Block access to sensitive files
    location ~ /(?:composer\.(?:json|lock)|\.env(?:\..*)?) { deny all; }

    # Symfony front controller
    location / {
        try_files $uri /index.php$is_args$args;
    }

    # Production: only execute index.php
    location ~ ^/index\.php(/|$) {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_split_path_info ^(.+\.php)(/.*)$;
        include fastcgi_params;

        # Use realpath_root for symlinked deployments
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $realpath_root;
        fastcgi_param HTTP_PROXY "";

        # Performance
        fastcgi_buffer_size 128k;
        fastcgi_buffers 4 256k;
        fastcgi_busy_buffers_size 256k;
        fastcgi_read_timeout 300;

        # Prevents direct access to index.php/path
        internal;
    }

    # Block all other PHP files
    location ~ \.php$ {
        return 404;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Bundles assets (legacy)
    location /bundles {
        try_files $uri =404;
    }
}
```

---

## Development Configuration

Add this block **only in development**:

```nginx
# DEV ONLY - Remove in production!
location ~ ^/index\.php(/|$) {
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    fastcgi_split_path_info ^(.+\.php)(/.*)$;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
    fastcgi_param DOCUMENT_ROOT $realpath_root;
    fastcgi_param HTTP_PROXY "";

    # Enable Symfony debug toolbar
    fastcgi_param APP_ENV dev;
    fastcgi_param APP_DEBUG 1;

    # No caching in dev
    fastcgi_no_cache 1;
    fastcgi_cache_bypass 1;
}
```

---

## Symfony Flex with Webpack Encore

```nginx
server {
    # ... SSL and base config ...

    root /var/www/project/public;

    # Webpack Encore assets (built files)
    location /build {
        try_files $uri =404;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Hot module replacement (dev only)
    location /build/hot {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        try_files $uri /index.php$is_args$args;
    }

    location ~ ^/index\.php(/|$) {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $realpath_root;
        internal;
    }

    location ~ \.php$ {
        return 404;
    }
}
```

---

## API Platform / Symfony API

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name api.example.com;

    root /var/www/api/public;

    # SSL config...

    # CORS headers (adjust origins as needed)
    add_header 'Access-Control-Allow-Origin' 'https://app.example.com' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, Accept' always;

    # Preflight requests
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Max-Age' 1728000;
        add_header 'Content-Type' 'text/plain; charset=utf-8';
        add_header 'Content-Length' 0;
        return 204;
    }

    location / {
        try_files $uri /index.php$is_args$args;
    }

    location ~ ^/index\.php(/|$) {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $realpath_root;

        # JSON responses
        fastcgi_param HTTP_ACCEPT "application/ld+json, application/json";

        internal;
    }

    location ~ \.php$ {
        return 404;
    }
}
```

---

## Performance Optimization

### FastCGI Caching

```nginx
# Define cache (http block)
fastcgi_cache_path /var/cache/nginx/symfony
    levels=1:2
    keys_zone=symfony:100m
    inactive=60m
    max_size=1g;

server {
    set $no_cache 0;

    # Don't cache authenticated requests
    if ($http_authorization != "") { set $no_cache 1; }
    if ($http_cookie ~* "PHPSESSID") { set $no_cache 1; }

    # Don't cache admin
    if ($request_uri ~* "^/admin") { set $no_cache 1; }

    location ~ ^/index\.php(/|$) {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $realpath_root;

        # Caching
        fastcgi_cache symfony;
        fastcgi_cache_valid 200 10m;
        fastcgi_cache_bypass $no_cache;
        fastcgi_no_cache $no_cache;
        add_header X-Cache $upstream_cache_status;

        internal;
    }
}
```

### OPcache Preloading

For Symfony 5.1+, enable preloading in `php.ini`:

```ini
opcache.preload=/var/www/project/config/preload.php
opcache.preload_user=www-data
```

---

## Symfony CLI (Local Development)

For local development, Symfony CLI is often simpler than NGINX:

```bash
# Install Symfony CLI
curl -sS https://get.symfony.com/cli/installer | bash

# Start local server with HTTPS
symfony server:start

# Or use custom port
symfony server:start --port=8080
```

---

## Key Configuration Notes

| Setting | Purpose |
|---------|---------|
| `$realpath_root` | Resolves symlinks - essential for atomic deployments |
| `internal` | Prevents direct access to `/index.php/path` |
| Explicit PHP location | Only `index.php` is executed; all other PHP returns 404 |

!!! tip "Symlinked Deployments"
    When using deployment tools like Deployer, Capistrano, or Ansistrano that use symlinks, always use `$realpath_root` instead of `$document_root`. This ensures OPcache detects file changes correctly during deployments.

---

## Deployment Checklist

- [ ] Remove any dev-only location blocks
- [ ] Verify `APP_ENV=prod` in `.env.local.php`
- [ ] Ensure `.env` files are not accessible
- [ ] Test that `/index.php/some-path` returns 404
- [ ] Run `composer install --no-dev --optimize-autoloader`
- [ ] Run `bin/console cache:clear --env=prod`
- [ ] Run `bin/console cache:warmup --env=prod`

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 404 on all routes | Check `try_files` includes `$is_args$args` |
| Assets not loading | Ensure `/build` location exists if using Encore |
| OPcache stale after deploy | Use `$realpath_root` or clear OPcache |
| Slow first request | Enable OPcache preloading |
| Session issues | Check PHP-FPM session handler configuration |

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [CodeIgniter Configuration](codeigniter.md)
- [FastCGI Examples](../examples/fastcgi.md)
