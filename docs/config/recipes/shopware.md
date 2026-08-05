---
title: NGINX Shopware Configuration Guide
description: Production-ready NGINX configuration for Shopware e-commerce platform with static file caching and HTTP/2 push support.
keywords: nginx, shopware, e-commerce, ecommerce, online store, php, shopping cart, open source ecommerce
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - shopware
  - e-commerce
  - php
  - online store
---

# Shopware

Shopware is an open-source e-commerce platform written in PHP.

## Requirements

- [PHP-FPM](php-fpm.md)

## Configuration

```nginx
server {
    listen 80;
    index index.php;
    server_name example.com;
    root /var/www/html/public;

    # Needed for Shopware install/update
    location /recovery/install {
        index index.php;
        try_files $uri /recovery/install/index.php$is_args$args;
    }

    location /recovery/update/ {
        if (!-e $request_filename) {
            rewrite . /recovery/update/index.php last;
        }
    }

    # Static files with caching
    location ~* ^.+\.(?:css|cur|js|jpe?g|gif|ico|png|svg|webp|html|woff|woff2|xml)$ {
        expires 1y;
        add_header Cache-Control "public, must-revalidate, proxy-revalidate";
        access_log off;
        log_not_found off;
        tcp_nodelay off;

        open_file_cache max=3000 inactive=120s;
        open_file_cache_valid 45s;
        open_file_cache_min_uses 2;
        open_file_cache_errors off;
    }

    # Security: Script-src none for SVGs
    location ~* ^.+\.svg$ {
        add_header Content-Security-Policy "script-src 'none'";
    }

    # Forward to index.php
    location / {
        try_files $uri /index.php$is_args$args;
    }

    # PHP handling
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        include fastcgi.conf;
        fastcgi_param HTTP_PROXY "";
        fastcgi_buffers 8 16k;
        fastcgi_buffer_size 32k;
        fastcgi_read_timeout 300s;
        client_body_buffer_size 128k;
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        http2_push_preload on;
    }
}
```
