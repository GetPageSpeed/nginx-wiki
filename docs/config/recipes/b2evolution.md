---
title: NGINX b2evolution CMS Configuration Guide
description: Configure NGINX for b2evolution CMS with blog, photo gallery, forum support, REST API routing, and static file caching.
keywords: nginx, b2evolution, cms, blog, photo gallery, forum, php, content management, rest api
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - b2evolution
  - cms
  - blog
  - php
  - rest api
---

# b2evolution

b2evolution is a Content Management System (CMS) for blogs, photo galleries, forums, and community sites.

## Configuration

```nginx
server {
    listen 80;
    server_name b2evolution.blog www.b2evolution.blog;
    root /var/www/b2evolution;
    index index.php index.htm index.html;

    location / {
        index index.php;
        try_files $uri $uri/ @b2evo;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        try_files $uri /htsrv/getfile.php?$args;
        expires max;
        log_not_found off;
    }

    location @b2evo {
        rewrite ^(.*) /index.php?$1 last;
    }

    # REST API
    location /api/ {
        auth_basic off;
        rewrite "^/api/v(?<version>[^/]+)/(?<parameters>(.+))$" 
            /htsrv/rest.php?api_version=$version&api_request=$parameters last;
    }

    location ~ \.php$ {
        include /etc/nginx/fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass unix:/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```
