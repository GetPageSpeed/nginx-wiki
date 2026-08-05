---
title: NGINX Server Blocks and Virtual Hosts Configuration
description: Configure NGINX server blocks for virtual hosting with wildcards, default servers, SSL/TLS, and server_name selection logic examples.
keywords: nginx server blocks, nginx virtual hosts, nginx server_name, nginx default_server, nginx wildcard, nginx vhost
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - server blocks
  - virtual hosts
  - server_name
  - configuration
---

# Server Blocks

!!! note "Terminology"
    "VirtualHost" is an Apache term. NGINX uses **Server Blocks** that bind to TCP sockets via the `server_name` and `listen` directives.

---

## Two Server Blocks, Serving Static Files

```nginx
http {
    index index.html;

    server {
        server_name www.domain1.com;
        access_log logs/domain1.access.log main;
        root /var/www/domain1.com/htdocs;
    }

    server {
        server_name www.domain2.com;
        access_log logs/domain2.access.log main;
        root /var/www/domain2.com/htdocs;
    }
}
```

---

## Default "Catch All" Server Block

```nginx
http {
    index index.html;

    server {
        listen 80 default_server;
        server_name _;  # Invalid value that never matches a real hostname
        access_log logs/default.access.log main;

        server_name_in_redirect off;

        root /var/www/default/htdocs;
    }
}
```

!!! info "`server_name _`"
    The underscore is a convention for a "catch-all" that never matches real hostnames. Any invalid value works.

---

## Wildcard Subdomains in a Parent Folder

Easily add new subdomains or domains automatically when DNS records point to the server:

```nginx
server {
    listen 80 default_server;
    server_name star.yourdomain.com *.yourdomain.com;

    root /PATH/TO/WEBROOT;

    error_page 404 errors/404.html;
    access_log logs/star.yourdomain.com.access.log;

    index index.php index.html index.htm;

    # Static files: no logging, maximum cache
    location ~* \.(jpg|jpeg|gif|css|png|js|ico|html)$ {
        access_log off;
        expires max;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_intercept_errors on;
        fastcgi_pass 127.0.0.1:9000;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

---

## Server Block Selection Logic

NGINX selects a server block using this priority:

1. **Exact match** on `server_name`
2. **Wildcard at start** (`*.example.com`)
3. **Wildcard at end** (`www.example.*`)
4. **Regex match** (`~^www\d+\.example\.com$`)
5. **`default_server`** on the matching `listen` directive

```nginx
# These are evaluated in order of specificity
server_name example.com;              # Exact match (highest priority)
server_name *.example.com;            # Leading wildcard
server_name www.example.*;            # Trailing wildcard
server_name ~^www\d+\.example\.com$;  # Regex
```

---

## SSL/TLS Server Blocks

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com www.example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    root /var/www/example.com;
    index index.html;
}
```

---

## Per-Domain Access Logs

```nginx
server {
    server_name example.com;
    access_log /var/log/nginx/example.com.access.log;
    error_log /var/log/nginx/example.com.error.log;
    # ...
}
```


