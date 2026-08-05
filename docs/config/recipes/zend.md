---
title: NGINX Zend Framework Configuration Guide
description: Configure NGINX with Zend Framework PHP applications using PHP-FPM and Zend Server for MVC web development.
keywords: nginx, zend framework, zend server, php, mvc framework, php-fpm, fastcgi, enterprise php
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - zend framework
  - php
  - mvc
  - zend server
---

# Zend Framework

The Zend Framework is an MVC framework that provides all components required for most web applications.

## Requirements

- Zend Server or standalone Zend Framework with PHP-FPM

---

## Configuration

```nginx
server {
    listen 80;
    server_name www.example.com;
    root /var/www/www.example.com/myapplication;
    index index.html index.htm index.php;

    location / {
        try_files $uri $uri/ /index.php$is_args$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/usr/local/zend/tmp/php-fastcgi.socket;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }
}
```

!!! note "Zend Server 6.1+"
    Starting with Zend Server 6.1, NGINX is natively supported. Use the automated installer:
    ```bash
    ./install_zs.sh <PHP Version> nginx
    ```
