---
title: NGINX PmWiki Configuration Guide
description: Configure NGINX for PmWiki collaborative wiki system with URL rewriting, static file caching, and security settings.
keywords: nginx, pmwiki, wiki, collaborative wiki, php, url rewriting, documentation, cms
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - pmwiki
  - wiki
  - php
  - collaborative
---

# PmWiki

PmWiki is a wiki-based system for collaborative creation and maintenance of websites.

## Requirements

- [PHP-FPM](php-fpm.md)

## Configuration

```nginx
server {
    server_name wiki.example.com;
    root /srv/www/pmwiki/public;
    index pmwiki.php;

    # Block access to sensitive directories
    location ~ ^/(cookbook|local|scripts|wiki.d|wikilib.d) {
        deny all;
    }

    location / {
        try_files $uri $uri/ @pmwiki;
    }

    location @pmwiki {
        rewrite ^/(.*) /pmwiki.php?n=$1;
    }

    # PHP handling
    location ~ \.php$ {
        include /etc/nginx/fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass unix:/run/php-fpm/php-fpm.sock;
    }

    # Cache static files
    location ~* \.(?:ico|css|js|gif|jpe?g|png)$ {
        expires max;
        add_header Pragma public;
        add_header Cache-Control "public, must-revalidate, proxy-revalidate";
    }

    # Drop common log entries
    location = /robots.txt { access_log off; log_not_found off; }
    location = /favicon.ico { access_log off; log_not_found off; }
    location ~ /\. { access_log off; log_not_found off; deny all; }
    location ~ ~$ { access_log off; log_not_found off; deny all; }
}
```
