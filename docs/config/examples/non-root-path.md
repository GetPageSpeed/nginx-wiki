---
title: NGINX FastCGI Configuration for Non-Root Web Paths
description: Configure NGINX FastCGI for applications in subdirectories with proper PATH_INFO and SCRIPT_NAME parameters like Apache FastCGI.
keywords: nginx fastcgi path, nginx subdirectory, nginx path_info, nginx script_name, nginx non-root, nginx fastcgi subdirectory
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - fastcgi
  - path_info
  - subdirectory
  - configuration
---

# Non-Root Web Path

When installing FastCGI applications in a non-root path (e.g., `http://example.com/myapp/`), some applications expect `PATH_INFO` and `SCRIPT_NAME` parameters similar to Apache.

---

## Apache Equivalent

```apache
FastCgiExternalServer /var/www/myapp -socket /path/to/myapp.sock
```

---

## NGINX Configuration

```nginx
location ~ /myapp(?<path_info>/.*|$) {
    fastcgi_pass unix:/path/to/myapp.sock;
    include /etc/nginx/fastcgi_params;

    fastcgi_param PATH_INFO $path_info;
    fastcgi_param SCRIPT_NAME "/myapp";
}
```

---

## How It Works

| Request | `PATH_INFO` | `SCRIPT_NAME` |
|---------|-------------|---------------|
| `/myapp/` | `/` | `/myapp` |
| `/myapp/page` | `/page` | `/myapp` |
| `/myapp/api/users` | `/api/users` | `/myapp` |

---

## Compatible Applications

This configuration works with:

- Mercurial (`hgweb.cgi`)
- Trac
- Zope (via FastCGI)
- Many Python WSGI applications

