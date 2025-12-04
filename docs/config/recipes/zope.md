---
title: Zope via FastCGI
description: Using NGINX as a front-end for Zope via FastCGI.
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


