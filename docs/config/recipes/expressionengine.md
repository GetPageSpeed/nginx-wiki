---
title: NGINX ExpressionEngine Configuration Guide
description: Configure NGINX for ExpressionEngine CMS with PATH_INFO support, clean URLs, and duplicate content prevention.
keywords: nginx, expressionengine, cms, content management, path info, clean urls, php, url rewriting
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - expressionengine
  - cms
  - php
  - path info
  - clean urls
---

# ExpressionEngine

ExpressionEngine is a flexible content management system.

## Configuration

```nginx
server {
    listen 80;
    server_name www.example.com;
    root /var/www/expressionengine;

    access_log /var/log/nginx/ee-access.log;
    error_log /var/log/nginx/ee-error.log;

    location / {
        index index.php;
        try_files $uri $uri/ @ee;
    }

    location @ee {
        rewrite ^(.*) /index.php?$1 last;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

## With PATH_INFO Support

For URLs like `/index.php/your-path`:

```nginx
location /index.php {
    include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    set $script $uri;
    set $path_info $uri;

    if ($args ~* "^(/.+)$") {
        set $path_info $1;
    }

    fastcgi_pass 127.0.0.1:9000;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_param PATH_INFO $path_info;
}
```

## Prevent Duplicate Content

```nginx
location /index.php {
    if ($request_uri ~ "^/index\.php/") {
        return 404;
    }
    # ... rest of config
}
```


