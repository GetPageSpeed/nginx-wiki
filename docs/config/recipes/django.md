---
title: NGINX Django Configuration Guide
description: Production-ready NGINX configuration for Django with Gunicorn or uWSGI, including WebSocket support via Django Channels.
keywords: nginx, django, python, gunicorn, uwsgi, wsgi, websocket, django channels, static files, reverse proxy
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - django
  - python
  - gunicorn
  - uwsgi
  - websocket
---

# Django

Production-ready NGINX configuration for Django applications with Gunicorn or uWSGI.

---

## With Gunicorn (Recommended)

```nginx
upstream django {
    server unix:/run/gunicorn/myproject.sock fail_timeout=0;
    keepalive 32;
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com www.example.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/django.access.log;
    error_log /var/log/nginx/django.error.log;

    # Max upload size
    client_max_body_size 50m;

    # Static files (collected via collectstatic)
    location /static/ {
        alias /var/www/myproject/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files (user uploads)
    location /media/ {
        alias /var/www/myproject/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 300;
    }
}
```

### Gunicorn Configuration

`gunicorn.conf.py`:

```python
import multiprocessing

bind = "unix:/run/gunicorn/myproject.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

### Systemd Service

`/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn Django Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/myproject
ExecStart=/var/www/myproject/venv/bin/gunicorn \
    --config gunicorn.conf.py \
    myproject.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## With uWSGI

```nginx
upstream django {
    server unix:/run/uwsgi/myproject.sock;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    # SSL config...

    location /static/ {
        alias /var/www/myproject/staticfiles/;
        expires 1y;
    }

    location /media/ {
        alias /var/www/myproject/media/;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass django;
        uwsgi_read_timeout 300;
    }
}
```

### uWSGI Configuration

`uwsgi.ini`:

```ini
[uwsgi]
chdir = /var/www/myproject
module = myproject.wsgi:application
master = true
processes = 4
threads = 2
socket = /run/uwsgi/myproject.sock
chmod-socket = 660
vacuum = true
die-on-term = true
max-requests = 1000
harakiri = 120
```

---

## Django Settings

`settings.py`:

```python
# Security settings for NGINX proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/myproject/staticfiles/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/myproject/media/'

# Security
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Run collectstatic:

```bash
python manage.py collectstatic --noinput
```

---

## WebSocket Support (Django Channels)

```nginx
upstream django_http {
    server unix:/run/gunicorn/myproject.sock;
}

upstream django_ws {
    server 127.0.0.1:8001;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    # SSL config...

    location /static/ {
        alias /var/www/myproject/staticfiles/;
    }

    # WebSocket endpoint
    location /ws/ {
        proxy_pass http://django_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # HTTP requests
    location / {
        proxy_pass http://django_http;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Run Daphne for WebSocket:

```bash
daphne -b 127.0.0.1 -p 8001 myproject.asgi:application
```

---

## Performance Tips

### Enable Response Caching

```nginx
proxy_cache_path /var/cache/nginx/django
    levels=1:2
    keys_zone=django:10m
    inactive=60m
    max_size=1g;

server {
    location / {
        proxy_cache django;
        proxy_cache_valid 200 10m;
        proxy_cache_bypass $http_authorization;
        add_header X-Cache-Status $upstream_cache_status;
        
        proxy_pass http://django;
        # ... other proxy settings
    }
}
```

### Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json application/javascript
           application/xml application/rss+xml image/svg+xml;
```

---

## See Also

- [Python (Flask/FastAPI)](pylons.md)
- [Ruby Applications](ruby.md)
