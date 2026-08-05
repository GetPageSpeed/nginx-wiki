---
title: NGINX UVdesk Helpdesk Configuration Guide
description: Configure NGINX for UVdesk open-source Symfony helpdesk system by Webkul with PHP-FPM and clean URL support.
keywords: nginx, uvdesk, helpdesk, symfony, support ticket, customer support, php, webkul, open source
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - uvdesk
  - helpdesk
  - symfony
  - php
  - support ticket
---

# UVdesk

UVdesk is an open-source helpdesk built on Symfony by Webkul.

## Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/example.com/public;

    index index.html index.htm index.php;

    location / {
        autoindex on;
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;

        location ~ /\.ht {
            deny all;
        }
    }
}
```


