---
title: Zend Framework
description: A sample NGINX configuration for Zend Framework.
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
