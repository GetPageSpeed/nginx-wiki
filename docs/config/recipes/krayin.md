---
title: NGINX Krayin CRM Configuration Guide
description: Configure NGINX for Krayin open-source Laravel and Vue.js CRM by Webkul with security headers and PHP-FPM setup.
keywords: nginx, krayin, crm, laravel, vue.js, customer relationship management, webkul, php, open source
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - krayin
  - crm
  - laravel
  - vue.js
  - php
---

# Krayin CRM

Krayin is an open-source Laravel + Vue.js CRM by Webkul.

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


