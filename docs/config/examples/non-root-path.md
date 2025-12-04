---
title: Non-Root Web Path
description: FastCGI configuration for applications installed in a subdirectory.
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

