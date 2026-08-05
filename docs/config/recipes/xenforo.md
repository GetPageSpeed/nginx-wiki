---
title: NGINX XenForo Configuration Guide
description: Production-ready NGINX configuration for XenForo 2.x forum software with friendly URLs, WebSocket support, and security.
keywords: nginx, xenforo, forum software, php, friendly urls, websocket, community forum, bulletin board
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - xenforo
  - forum
  - php
  - websocket
  - security
---

# XenForo

Production-ready NGINX configuration for XenForo 2.x forum software.

---

## Basic Configuration

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name forum.example.com;

    root /var/www/xenforo;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/forum.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forum.example.com/privkey.pem;

    # Upload limits (for attachments)
    client_max_body_size 100m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Friendly URLs
    location / {
        try_files $uri $uri/ /index.php?$uri&$args;
    }

    # PHP handling
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        include fastcgi_params;
        fastcgi_read_timeout 120;
    }

    # Block sensitive directories
    location ^~ /internal_data/ { deny all; }
    location ^~ /library/ { deny all; }
    location ^~ /src/ { deny all; }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
```

---

## XenForo Configuration

In Admin CP → Options → Basic Board Information:

- Set **Board URL** to `https://forum.example.com`
- Enable **Use Full Friendly URLs**

---

## Add-on Paths

If using add-ons that require specific paths:

```nginx
# WebSocket support (for push notifications)
location /ws {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

---

## Security

```nginx
# Block PHP execution in data directories
location ~* /data/.*\.php$ { deny all; }

# Rate limit login
limit_req_zone $binary_remote_addr zone=xf_login:10m rate=1r/s;

location = /index.php {
    if ($arg_login) {
        limit_req zone=xf_login burst=5 nodelay;
    }
    
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
