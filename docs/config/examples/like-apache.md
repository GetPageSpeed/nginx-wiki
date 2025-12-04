---
title: Apache-like Configurations
description: NGINX equivalents for common Apache configurations.
---

# Apache-like Configurations

## ProxyPassReverse Equivalent

### Apache

```apache
<VirtualHost myhost:80>
    ServerName myhost
    DocumentRoot /path/to/myapp/public
    ProxyPass / http://myapp:8080/
    ProxyPassReverse / http://myapp:8080/
</VirtualHost>
```

### NGINX

NGINX doesn't have `ProxyPassReverse`, but you can achieve the same result with headers:

```nginx
server {
    listen myhost:80;
    server_name myhost;

    location / {
        root /path/to/myapp/public;
        proxy_set_header X-Forwarded-Host $host:$server_port;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://myapp:8080;
    }
}
```

!!! note
    For location header rewriting, you may also need `proxy_redirect`.

---

## Common Apache to NGINX Translations

| Apache | NGINX |
|--------|-------|
| `DocumentRoot` | `root` |
| `ServerName` | `server_name` |
| `<VirtualHost>` | `server { }` |
| `<Directory>` | `location` |
| `Options -Indexes` | `autoindex off` |
| `ErrorDocument 404` | `error_page 404` |
| `Allow from all` | (default behavior) |
| `Deny from all` | `deny all` |
| `RewriteRule` | `rewrite` or `try_files` |
| `ProxyPass` | `proxy_pass` |

---

## .htaccess Equivalent

NGINX doesn't support `.htaccess` files. All configuration must be in the server config.

### Apache .htaccess

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php/$1 [L]
```

### NGINX

```nginx
location / {
    try_files $uri $uri/ /index.php$is_args$args;
}
```
