---
title: NGINX Pylons Framework Configuration
description: Configure NGINX with Pylons Python web framework using Flup FastCGI for production deployment and request handling.
keywords: nginx, pylons, python, fastcgi, flup, web framework, wsgi, python web development
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - pylons
  - python
  - fastcgi
  - flup
---

# Pylons

## Pylons Configuration

Edit your project INI file (`development.ini`) and change `[server:main]`:

```ini
[server:main]
use = egg:Flup#fcgi_thread
host = 0.0.0.0
port = 8080
```

Install Flup if needed:

```bash
easy_install flup
```

## NGINX Configuration

```nginx
server {
    server_name domain.tld;

    location / {
        fastcgi_pass 127.0.0.1:8080;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass_header Authorization;
        fastcgi_intercept_errors off;
    }
}
```
