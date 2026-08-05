---
title: NGINX iRedMail Configuration Guide
description: Configure NGINX for iRedMail mail server with SSL/TLS webmail, iRedAdmin Python panel via uWSGI, and secure PHP handling.
keywords: nginx, iredmail, mail server, webmail, uwsgi, ssl, tls, email server, php, python
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - iredmail
  - mail server
  - webmail
  - ssl
  - uwsgi
---

# iRedMail

## Requirements

- [PHP-FPM](php-fpm.md)

## Webmail Configuration

```nginx
server {
    listen 80;
    server_name mail.example.com;

    location / {
        rewrite ^ https://mail.example.com/webmail permanent;
    }
}

server {
    listen 443 ssl;
    server_name mail.example.com;

    ssl_certificate /etc/ssl/certs/iRedMail_CA.pem;
    ssl_certificate_key /etc/ssl/private/iRedMail.key;
    ssl_session_timeout 5m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        root /usr/share/apache2/;
        index index.php index.html;
    }

    location ~ \.php$ {
        root /usr/share/apache2/;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /usr/share/apache2$fastcgi_script_name;
        fastcgi_param SERVER_NAME $http_host;
        fastcgi_ignore_client_abort on;
    }
}
```

## iRedAdmin (Python Admin Panel)

```nginx
server {
    listen 443 ssl;
    server_name mail.example.com;

    ssl_certificate /etc/nginx/ssl/cert.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    location / {
        root /var/www/iredadmin/;
        uwsgi_pass unix:///var/run/uwsgi/app/iredadmin/iredadmin.socket;
        uwsgi_param UWSGI_PYHOME /var/www/iredadmin/python-home;
        uwsgi_param UWSGI_CHDIR /var/www/iredadmin;
        uwsgi_param UWSGI_SCRIPT iredadmin;
        include uwsgi_params;
    }

    location /static {
        alias /var/www/iredadmin/static/;
    }

    location ~ /\.ht {
        deny all;
    }
}
```


