---
title: MoinMoin Wiki
description: A sample NGINX configuration for MoinMoin wiki.
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
