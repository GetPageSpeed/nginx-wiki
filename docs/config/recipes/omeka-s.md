---
title: NGINX Omeka S Configuration Guide
description: Configure NGINX for Omeka S digital collections and publishing platform with admin routing, security, and static caching.
keywords: nginx, omeka s, digital collections, museum, archives, semantic web, php, linked data, exhibitions
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - omeka s
  - digital collections
  - museum
  - php
  - semantic web
---

# Omeka S

## Configuration

```nginx
server {
    server_name omeka.example.com;
    root /var/www/omeka;

    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    # Block PHP in subdirectories
    location ~ \..*/.*\.php$ {
        return 403;
    }

    location / {
        try_files $uri /index.php?$args;
    }

    location /admin {
        try_files $uri /index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors on;
        fastcgi_pass 127.0.0.1:9000;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires max;
        log_not_found off;
    }
}
```

!!! note
    Set `cgi.fix_pathinfo = 0` in php.ini.


