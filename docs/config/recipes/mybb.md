---
title: NGINX MyBB Forum Configuration Guide
description: Configure NGINX for MyBB free forum software with PHP-FPM, secure file handling, and protection for sensitive directories.
keywords: nginx, mybb, forum software, php, bulletin board, free forum, fastcgi, community software
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - mybb
  - forum
  - php
  - security
---

# MyBB

## Configuration

```nginx
server {
    server_name forum.example.com;
    access_log logs/forum.access;
    error_log logs/forum.error error;
    root /var/www/mybb;

    location / {
        index index.php;
    }

    # Deny access to internal files
    location ~ /(inc|uploads/avatars) {
        deny all;
    }

    # PHP handling
    location ~ \.php$ {
        fastcgi_pass unix:/tmp/php.socket;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }
}
```

!!! warning "Security Note"
    Set `cgi.fix_pathinfo=0` in php.ini to prevent the path info security vulnerability where uploaded files like `pic.gif/foo.php` could be executed as PHP.

See the [PHP-FPM guide](php-fpm.md) for details on setting up the PHP socket.
