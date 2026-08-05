---
title: NGINX SilverStripe CMS Configuration Guide
description: Configure NGINX for SilverStripe 4.1+ PHP CMS framework with security hardening and FastCGI buffer optimization.
keywords: nginx, silverstripe, cms, php framework, content management, fastcgi, php-fpm, security
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - silverstripe
  - cms
  - php
  - framework
  - security
---

# SilverStripe

SilverStripe is a modern PHP-based CMS Framework.

## Requirements

- PHP-FPM or FastCGI listening on `127.0.0.1:9000`
- SilverStripe 4.1+ (see official docs for earlier versions)

## Setup

1. Remove the `.htaccess` file and `index.php` in your SilverStripe installation root
2. Apply the following configuration

---

## Configuration

```nginx
server {
    include mime.types;
    default_type application/octet-stream;
    client_max_body_size 0;  # Manage in php.ini (upload_max_filesize & post_max_size)
    
    listen 80;
    root /path/to/ss/folder/public;
    server_name example.com www.example.com;

    # Defend against SS-2015-013
    if ($http_x_forwarded_host) {
        return 400;
    }

    location / {
        try_files $uri /index.php?$query_string;
    }

    error_page 404 /assets/error-404.html;
    error_page 500 /assets/error-500.html;
    error_page 502 /assets/error-500.html;
    error_page 503 /assets/error-500.html;

    location ^~ /assets/ {
        sendfile on;
        try_files $uri =404;
    }

    location /index.php {
        fastcgi_buffer_size 32k;
        fastcgi_busy_buffers_size 64k;
        fastcgi_buffers 4 32k;
        fastcgi_keep_conn on;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }
}
```

---

## Security

The `if ($http_x_forwarded_host)` block defends against SS-2015-013, a security vulnerability related to Host header injection.

