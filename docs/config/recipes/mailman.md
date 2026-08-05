---
title: NGINX GNU Mailman Configuration Guide
description: Configure NGINX for GNU Mailman mailing list manager with clean URLs, pipermail archives, and CGI backend integration.
keywords: nginx, mailman, mailing list, email list, newsletter, cgi, pipermail, discussion list
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - mailman
  - mailing list
  - email
  - cgi
  - pipermail
---

# Mailman

Mailman is free software for managing email discussion and newsletter lists.

## Configuration

```nginx
server {
    listen 80;
    server_name lists.example.com;
    root /usr/lib;

    location = / {
        rewrite ^ /mailman/listinfo permanent;
    }

    location / {
        rewrite ^ /mailman$uri?$args;
    }

    location = /mailman/ {
        rewrite ^ /mailman/listinfo permanent;
    }

    location /mailman/ {
        include proxy_params;
        proxy_pass http://127.0.0.1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /cgi-bin {
        rewrite ^/cgi-bin(.*)$ $1 permanent;
    }

    location /images/mailman {
        alias /var/lib/mailman/icons;
    }

    location /pipermail {
        alias /var/lib/mailman/archives/public;
        autoindex on;
    }
}
```

## CGI Backend (thttpd)

`/etc/thttpd/thttpd.conf`:

```
host=127.0.0.1
port=80
dir=/usr/lib/cgi-bin/mailman
nochroot
user=www-data
cgipat=/**
throttles=/etc/thttpd/throttle.conf
logfile=/var/log/thttpd.log
```

## Removing /cgi-bin/ from URLs

Edit `/usr/lib/mailman/Mailman/mm_cfg.py`:

```python
DEFAULT_URL_PATTERN = 'http://%s/mailman/'
PRIVATE_ARCHIVE_URL = '/mailman/private'
```

## Fix Authentication Issues

If you need to authenticate for every link after migrating:

```bash
while read list stuff; do withlist -l -r fix_url "$list"; done < <(list_lists)
```


