---
title: NGINX Zope Configuration via FastCGI
description: Configure NGINX as a front-end for Zope and Plone Python application server using FastCGI with PATH_INFO handling.
keywords: nginx, zope, plone, python, fastcgi, cms, python cms, content management, path info
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - zope
  - plone
  - python
  - fastcgi
  - cms
---

# Zope via FastCGI

## Configuration

```nginx
location ~ /zope(?<path_info>/.*|$) {
    fastcgi_pass unix:/var/run/plone-site.sock;
    include /etc/nginx/fastcgi_params;
        fastcgi_param HTTP_PROXY "";

    set $fixed_content_length $content_length;
    if ($fixed_content_length = "") {
        set $fixed_content_length "0";
    }

    fastcgi_param CONTENT_LENGTH $fixed_content_length;
    fastcgi_param PATH_INFO $path_info;
    fastcgi_param SCRIPT_NAME /zope;
}
```

!!! note
    Use `location ~ /zope(/|$)` if URLs without trailing slash (e.g., `/zope`) should also work.

!!! warning "CONTENT_LENGTH"
    Zope calls `atoi` on `CONTENT_LENGTH`, so an empty string causes `ValueError`. Always set it to "0" when empty.


