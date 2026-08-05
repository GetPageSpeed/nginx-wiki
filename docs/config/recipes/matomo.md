---
title: NGINX Matomo Analytics Configuration Guide
description: Secure NGINX configuration for Matomo (formerly Piwik) web analytics platform with protected directories and PHP handling.
keywords: nginx, matomo, piwik, web analytics, analytics platform, php, google analytics alternative, privacy
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - matomo
  - analytics
  - php
  - privacy
  - security
---

# Matomo (Piwik)

See the [complete official configuration](https://github.com/matomo-org/matomo-nginx).

## Configuration

```nginx
server {
    listen [::]:80;
    server_name www.stats.example.com;
    rewrite ^ $scheme://stats.example.com$request_uri? permanent;
}

server {
    listen [::]:80;
    limit_conn arbeit 10;
    server_name stats.example.com;

    access_log /var/log/nginx/stats.example.com_access.log;
    error_log /var/log/nginx/stats.example.com_error.log;

    # Disable methods besides HEAD, GET, POST
    if ($request_method !~ ^(GET|HEAD|POST)$) {
        return 444;
    }

    root /var/www/sites/stats.example.com/;
    index index.php index.html;

    # Favicon handling
    location = /favicon.ico {
        try_files /favicon.ico =204;
    }

    # Try files, fallback to index.php
    location / {
        try_files $uri /index.php;
    }

    # PHP handling (only index.php and piwik.php)
    location ~* ^/(?:index|piwik)\.php$ {
        fastcgi_pass unix:/tmp/php-cgi/php-cgi.socket;
    }

    # Block protected directories
    location ~ /(?:config|tmp|vendor)/ {
        return 404;
    }

    # Block other PHP files
    location ~* ^.*\.php$ {
        return 404;
    }

    # Block hidden files/directories
    location ~ /\. {
        return 404;
    }

    # Block package manager configs
    location ~ (?:composer.json|composer.lock|bower.json)$ {
        return 404;
    }

    # Block text files
    location ~* (?:README|LICENSE|LEGALNOTICE|\.txt|\.md)$ {
        return 404;
    }
}
```
