---
title: Pylons
description: A sample NGINX configuration for Pylons Python framework.
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
