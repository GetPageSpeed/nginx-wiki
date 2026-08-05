---
title: NGINX Laravel Configuration Guide
description: Production-ready NGINX configuration for Laravel 10/11 with Octane, WebSockets, Horizon support, and API rate limiting.
keywords: nginx, laravel, php framework, octane, swoole, websockets, reverb, horizon, api, fastcgi
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - laravel
  - php
  - octane
  - websockets
  - api
---

# Laravel

Production-ready NGINX configuration for Laravel 10/11 applications.

---

## Basic Configuration

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

    root /var/www/laravel/public;
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
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/laravel.access.log;
    error_log /var/log/nginx/laravel.error.log;

    # Max upload size
    client_max_body_size 100m;

    # Deny hidden files (except .well-known)
    location ~ /\.(?!well-known) {
        deny all;
    }

    # Block access to sensitive files
    location ~* (?:\.(?:bak|conf|dist|fla|in[ci]|log|psd|sh|sql|sw[op])|~)$ {
        deny all;
    }

    # Front controller
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP handling
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_read_timeout 300;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Deny access to .env file
    location ~ /\.env {
        deny all;
    }
}
```

---

## Laravel with Octane (Swoole/RoadRunner)

For high-performance Laravel Octane:

```nginx
upstream octane {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    root /var/www/laravel/public;

    # SSL config...

    # Static files served directly
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Everything else to Octane
    location / {
        proxy_pass http://octane;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300;
    }
}
```

Start Octane:

```bash
php artisan octane:start --server=swoole --host=127.0.0.1 --port=8000
```

---

## Laravel WebSockets / Reverb

For Laravel Reverb or WebSockets:

```nginx
upstream websocket {
    server 127.0.0.1:8080;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    # ... base config ...

    # WebSocket endpoint
    location /app {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # Broadcasting auth
    location /broadcasting/auth {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        # PHP-FPM config...
    }
}
```

---

## Laravel Horizon (Queue Dashboard)

Protect Horizon dashboard:

```nginx
location /horizon {
    try_files $uri $uri/ /index.php?$query_string;

    # Optional: IP restriction
    # allow 10.0.0.0/8;
    # deny all;
}
```

---

## API Rate Limiting

```nginx
# Define rate limit zones
limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

server {
    # ... base config ...

    # API endpoints
    location /api {
        limit_req zone=api burst=20 nodelay;
        try_files $uri $uri/ /index.php?$query_string;
    }

    # Login rate limiting
    location = /login {
        limit_req zone=login burst=3 nodelay;
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        # PHP-FPM config...
    }
}
```

---

## FastCGI Caching

```nginx
# Cache zone (http block)
fastcgi_cache_path /var/cache/nginx/laravel
    levels=1:2
    keys_zone=laravel:100m
    inactive=60m
    max_size=1g;

server {
    set $skip_cache 0;

    # Don't cache authenticated requests
    if ($http_authorization != "") { set $skip_cache 1; }
    if ($http_cookie ~* "laravel_session") { set $skip_cache 1; }

    # Don't cache specific paths
    if ($request_uri ~* "^/(api|nova|horizon|telescope)") { set $skip_cache 1; }
    if ($request_method = POST) { set $skip_cache 1; }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;

        # Caching
        fastcgi_cache laravel;
        fastcgi_cache_valid 200 10m;
        fastcgi_cache_bypass $skip_cache;
        fastcgi_no_cache $skip_cache;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

---

## Laravel Configuration

### Trusted Proxies

In `app/Http/Middleware/TrustProxies.php`:

```php
protected $proxies = '*';

protected $headers =
    Request::HEADER_X_FORWARDED_FOR |
    Request::HEADER_X_FORWARDED_HOST |
    Request::HEADER_X_FORWARDED_PORT |
    Request::HEADER_X_FORWARDED_PROTO;
```

### .env Settings

```env
APP_URL=https://example.com
ASSET_URL=https://example.com

# For Octane
OCTANE_SERVER=swoole

# Session/Cookie security
SESSION_SECURE_COOKIE=true
```

---

## Deployment Checklist

```bash
# Optimize for production
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan event:cache

# Clear caches when deploying
php artisan optimize:clear
php artisan optimize
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 404 on all routes | Check `try_files` ends with `$query_string` |
| CSRF token mismatch | Ensure `APP_URL` matches actual URL |
| Mixed content | Set `ASSET_URL` to HTTPS URL |
| File uploads fail | Increase `client_max_body_size` and PHP limits |
| Session issues | Check cookie secure settings match HTTPS |

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [Symfony Configuration](symfony.md)
- [Security Hardening](../security.md)

