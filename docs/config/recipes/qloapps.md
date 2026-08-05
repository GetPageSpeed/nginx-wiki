---
title: NGINX QloApps Hotel Booking Configuration Guide
description: Configure NGINX for QloApps open-source hotel reservation and booking system with security headers and timeout settings.
keywords: nginx, qloapps, hotel booking, reservation system, hotel management, php, hospitality, booking engine
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - qloapps
  - hotel booking
  - reservation
  - php
  - hospitality
---

# QloApps

QloApps is an open-source hotel reservation and booking system.

## Configuration

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /path/to/QloApps;

    index index.php;

    # Redirect 404 to QloApps error page
    error_page 404 /index.php?controller=404;

    # Security headers
    add_header Strict-Transport-Security 'max-age=84600; includeSubDomains;';
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header X-Frame-Options "SAMEORIGIN";

    error_log /var/log/nginx/qloapps-error.log warn;
    access_log /var/log/nginx/qloapps-access.log combined;

    location = /favicon.ico { log_not_found off; access_log off; }
    location = /robots.txt { allow all; log_not_found off; access_log off; }

    # Block hidden files
    location ~ /\. {
        deny all;
    }

    # PHP handling
    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_index index.php;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    # Timeouts
    proxy_read_timeout 500;
    proxy_connect_timeout 500;
    proxy_send_timeout 500;
    fastcgi_read_timeout 500;
    fastcgi_connect_timeout 500;
    fastcgi_send_timeout 500;
}
```


