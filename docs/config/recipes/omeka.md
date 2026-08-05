---
title: NGINX Omeka Configuration Guide
description: Configure NGINX for Omeka digital collections platform with admin routing, clean URLs, and static file caching.
keywords: nginx, omeka, digital collections, museum, archives, php, cultural heritage, exhibitions
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - omeka
  - digital collections
  - museum
  - php
  - archives
---

# Omeka

Omeka is a web publishing platform for sharing digital collections and creating exhibitions.

---

## Configuration

```nginx
server {
    server_name omeka.domain.tld;
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

    location ~ \..*/.*\.php$ {
        return 403;
    }

    location / {
        try_files $uri /index.php?$args;
    }

    location /admin {
        try_files $uri /admin/index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        # NOTE: You should have "cgi.fix_pathinfo = 0;" in php.ini
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors on;
        fastcgi_pass unix:/tmp/phpfpm.sock;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires max;
        log_not_found off;
    }

    location /install {
        try_files $uri /install/index.php?$args;

        # Check that rewrites work
        location ~* /install/check-mod-rewrite([^/]*)\.html$ {
            rewrite ^ /install/mod-rewrite.php?enabled=true;
        }
    }
}
```

