---
title: NGINX Bagisto E-commerce Configuration Guide
description: Configure NGINX for Bagisto Laravel and Vue.js e-commerce framework with security headers and PHP-FPM integration.
keywords: nginx, bagisto, e-commerce, ecommerce, laravel, vue.js, webkul, online store, php
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - bagisto
  - e-commerce
  - laravel
  - vue.js
  - php
---

# Bagisto

Bagisto is a Laravel + Vue.js e-commerce framework by Webkul.

## Configuration

!!! warning
    Never move `index.php` to the project root. Serve from the `public/` directory only.

```nginx
server {
    listen 80;
    server_name example.com;
    root /srv/example.com/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;
    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```


