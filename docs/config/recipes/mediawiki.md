---
title: NGINX MediaWiki Configuration Guide
description: Production-ready NGINX configuration for MediaWiki with short URLs, Visual Editor support, and security hardening.
keywords: nginx, mediawiki, wiki, short urls, visual editor, parsoid, php, wikipedia, fastcgi
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - mediawiki
  - wiki
  - php
  - short urls
  - security
---

# MediaWiki

Production-ready NGINX configuration for MediaWiki with short URLs and security hardening.

---

## Basic Configuration

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name wiki.example.com;

    root /var/www/mediawiki;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/wiki.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wiki.example.com/privkey.pem;

    # Upload limits
    client_max_body_size 50m;
    client_body_timeout 60;

    # Short URLs
    location / {
        try_files $uri $uri/ @rewrite;
    }

    location @rewrite {
        rewrite ^/(.*)$ /index.php?title=$1&$args;
    }

    # REST API (MediaWiki 1.35+)
    location /rest.php {
        try_files $uri $uri/ /rest.php?$args;
    }

    # Block sensitive directories
    location ^~ /maintenance/ { return 403; }
    location ^~ /cache/ { deny all; }
    location ^~ /includes/ { deny all; }
    location ^~ /languages/ { deny all; }
    location ^~ /serialized/ { deny all; }

    # Block sensitive files
    location ~* ^/(LocalSettings|AdminSettings|\.htaccess) { deny all; }

    # PHP handling
    location ~ \.php$ {
        try_files $uri =404;
        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_read_timeout 300;
    }

    # Static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2)$ {
        try_files $uri /index.php;
        expires 30d;
        add_header Cache-Control "public";
        log_not_found off;
        access_log off;
    }

    # 1x1 pixel tracking gif
    location = /_.gif {
        expires max;
        empty_gif;
    }

    # Image thumbnails
    location ~ ^/images/thumb/ {
        try_files $uri $uri/ @thumb;
    }

    location @thumb {
        rewrite ^/images/thumb/[0-9a-f]/[0-9a-f][0-9a-f]/([^/]+)/([0-9]+)px-.*$ /thumb.php?f=$1&width=$2;
        rewrite ^/images/thumb/archive/[0-9a-f]/[0-9a-f][0-9a-f]/([^/]+)/([0-9]+)px-.*$ /thumb.php?f=$1&width=$2&archived=1;

        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root/thumb.php;
    }
}
```

---

## Short URL Setup

### NGINX Configuration

The configuration above enables short URLs (e.g., `/wiki/Page` instead of `/index.php?title=Page`).

### LocalSettings.php

```php
# Article path (short URLs)
$wgArticlePath = "/wiki/$1";
$wgUsePathInfo = true;

# Script path
$wgScriptPath = "";
$wgScript = "/index.php";
$wgRedirectScript = "/redirect.php";
```

---

## Visual Editor Support

For VisualEditor with Parsoid:

```nginx
# Parsoid REST API (internal)
location /api/rest_v1/ {
    proxy_pass http://127.0.0.1:8142/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# Or if using built-in Parsoid (MW 1.35+)
location ^~ /rest.php/v1/page/ {
    try_files $uri /rest.php?$args;
}
```

---

## Security Hardening

### Restrict Image Uploads

```nginx
# Only allow specific image types in uploads
location ^~ /images/ {
    location ~* \.(php|phtml|php3|php4|php5|phps)$ {
        deny all;
    }
}
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=mw_login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=mw_api:10m rate=10r/s;

location = /index.php {
    # Rate limit login attempts
    if ($arg_title = "Special:UserLogin") {
        limit_req zone=mw_login burst=5 nodelay;
    }
}

location = /api.php {
    limit_req zone=mw_api burst=50 nodelay;
    try_files $uri =404;
    include fastcgi_params;
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

---

## Performance Tips

### Enable Object Caching

In `LocalSettings.php`:

```php
# APCu caching (recommended)
$wgMainCacheType = CACHE_ACCEL;
$wgSessionCacheType = CACHE_DB;

# Or use Redis
$wgMainCacheType = CACHE_REDIS;
$wgRedisServers = ['127.0.0.1'];
```

### Static File Caching

```nginx
# Aggressive caching for resources
location /resources/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

location /extensions/ {
    location ~* \.(js|css|png|jpg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }
}
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Short URLs not working | Ensure `$wgUsePathInfo = true;` in LocalSettings.php |
| 404 on wiki pages | Check `location @rewrite` block |
| Image uploads fail | Increase `client_max_body_size` |
| Slow page renders | Enable object caching (APCu or Redis) |

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [FastCGI Examples](../examples/fastcgi.md)
