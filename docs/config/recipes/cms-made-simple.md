---
title: NGINX CMS Made Simple Configuration Guide
description: Configure NGINX for CMS Made Simple open-source content management system with clean URL support and PHP-FPM.
keywords: nginx, cms made simple, cmsms, cms, content management, php, clean urls, fastcgi
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - cms made simple
  - cms
  - php
  - content management
---

# CMS Made Simple

CMS Made Simple is an open-source content management system for the rest of us.

## Requirements

- [PHP-FPM](php-fpm.md)

---

## Configuration

```nginx
server {
    listen 80;
    server_name .domain.tld;
    root /var/www/cms;
    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php?page=$request_uri;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

