---
title: NGINX PyroCMS Configuration Guide
description: Configure NGINX for PyroCMS Laravel-based content management system with gzip compression and PHP-FPM pool setup.
keywords: nginx, pyrocms, cms, laravel, php, content management, gzip compression, php-fpm pool
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - pyrocms
  - cms
  - laravel
  - php
  - gzip
---

# PyroCMS

PyroCMS is a PHP CMS built on Laravel.

## PyroCMS Configuration

Edit `/installer/config/config.php`:

```php
$config['index_page'] = "";
$config['uri_protocol'] = "REQUEST_URI";
```

Edit `/system/cms/config/config.php`:

```php
$config['index_page'] = "";
$config['uri_protocol'] = "REQUEST_URI";
```

---

## NGINX Configuration

```nginx
server {
    listen 80;
    server_name domain.com;
    root /path/to/webroot;
    index index.php;

    access_log /path/to/logs/access.log main;
    error_log /path/to/logs/error.log;

    client_max_body_size 200M;

    gzip on;
    gzip_static on;
    gzip_http_version 1.0;
    gzip_disable "MSIE [1-6].";
    gzip_vary on;
    gzip_comp_level 9;
    gzip_proxied any;
    gzip_types text/plain text/css application/x-javascript text/xml 
               application/xml application/xml+rss text/javascript;

    fastcgi_buffers 8 16k;
    fastcgi_buffer_size 32k;
    fastcgi_read_timeout 180;

    location / {
        try_files $uri $uri/ /index.php;
    }

    location /installer {
        try_files $uri $uri/ /installer/index.php;
    }

    fastcgi_intercept_errors off;

    location ~* \.(?:ico|css|js|gif|jpe?g|png)$ {
        expires max;
        add_header Pragma public;
        add_header Cache-Control "public, must-revalidate, proxy-revalidate";
    }

    location ~ \.php {
        fastcgi_pass unix:/tmp/domain.sock;
        fastcgi_split_path_info ^(.+\.php)(.*)$;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # Common security rules
    location = /robots.txt  { access_log off; log_not_found off; }
    location = /favicon.ico { access_log off; log_not_found off; }
    location ~ /\.          { access_log off; log_not_found off; deny all; }
    location ~ ~$           { access_log off; log_not_found off; deny all; }
}
```

---

## PHP-FPM Pool Configuration

Create a pool configuration (e.g., `/etc/php-fpm.d/domain.conf`):

```ini
[domain]
listen = /tmp/domain.sock
listen.allowed_clients = 127.0.0.1

user = someuser
group = someuser

pm = dynamic
pm.max_children = 25
pm.start_servers = 2
pm.min_spare_servers = 2
pm.max_spare_servers = 25

php_admin_value[error_log] = /var/log/php-fpm/domain-error.log
php_admin_flag[log_errors] = on
php_admin_value[session.save_path] = /tmp/
```

