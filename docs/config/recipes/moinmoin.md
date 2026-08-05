---
title: NGINX MoinMoin Wiki Configuration Guide
description: Configure NGINX with MoinMoin Python wiki using uWSGI for static file serving and efficient wiki page handling.
keywords: nginx, moinmoin, wiki, python, uwsgi, wsgi, python wiki, collaborative wiki
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - moinmoin
  - wiki
  - python
  - uwsgi
---

# MoinMoin Wiki

## Configuration with uWSGI

In `moin.wsgi`:

```python
app = make_application(shared=False)
```

This lets NGINX serve static content directly.

In your MoinMoin config (`mywiki.py`):

```python
class Config(FarmConfig):
    url_prefix_static = '/path/to/MoinMoin/web/static/htdocs'
```

NGINX configuration:

```nginx
# Static files
location /path/to/MoinMoin/web/static/htdocs {
    alias /path/to/MoinMoin/web/static/htdocs;
}

# Wiki via uWSGI
location /wiki {
    gzip off;
    include uwsgi_params;
    uwsgi_param SCRIPT_NAME /wiki;
    uwsgi_modifier1 30;
    uwsgi_pass unix:/path/to/uwsgi.socket;
}
```

!!! note "uWSGI Configuration"
    uWSGI needs `--ignore-script-name` for MoinMoin, otherwise it interprets the script name as a literal path.
