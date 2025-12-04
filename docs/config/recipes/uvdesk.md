---
title: UVdesk
description: A sample NGINX configuration for UVdesk helpdesk.
---

# UVdesk

UVdesk is an open-source helpdesk built on Symfony by Webkul.

## Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/example.com/public;

    index index.html index.htm index.php;

    location / {
        autoindex on;
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;

        location ~ /\.ht {
            deny all;
        }
    }
}
```


