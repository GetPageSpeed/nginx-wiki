---
title: Qwebirc
description: A sample NGINX configuration for Qwebirc IRC client.
---

# Qwebirc

Qwebirc is a web-based IRC client with its own embedded server.

## Redirect Method

Simple redirect to Qwebirc's embedded server:

```nginx
server {
    listen 80;
    server_name webchat.example.com;
    return 301 $scheme://webchat.example.com:8080$request_uri;
}
```

## Reverse Proxy Method

Hide the port and proxy through NGINX:

```nginx
server {
    listen 80;
    server_name webchat.example.com;

    access_log /var/log/nginx/qwebirc.access.log;
    error_log /var/log/nginx/qwebirc.error.log;

    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_buffering off;

    location / {
        proxy_pass http://127.0.0.1:9090;
    }
}
```

### Qwebirc Configuration

Update `config.py` or `iris.conf`:

```ini
ARGS = -i 127.0.0.1 -p 9090
BASE_URL = "http://webchat.example.com/"
FORWARDED_FOR_HEADER = "x-forwarded-for"
FORWARDED_FOR_IPS = ["127.0.0.1"]
```


