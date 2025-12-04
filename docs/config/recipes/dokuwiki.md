---
title: DokuWiki
description: NGINX configuration for DokuWiki file-based wiki.
---

# DokuWiki

Production-ready NGINX configuration for DokuWiki, a file-based wiki that doesn't require a database.

---

## Basic Configuration

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name wiki.example.com;

    root /var/www/dokuwiki;
    index doku.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/wiki.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wiki.example.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Block sensitive directories
    location ^~ /conf/ { deny all; }
    location ^~ /data/ { deny all; }
    location ^~ /bin/  { deny all; }
    location ^~ /inc/  { deny all; }

    # Block hidden files
    location ~ /\. { deny all; }

    # Main location with URL rewriting
    location / {
        try_files $uri $uri/ @dokuwiki;
    }

    # DokuWiki URL rewrites
    location @dokuwiki {
        rewrite ^/_media/(.*)  /lib/exe/fetch.php?media=$1 last;
        rewrite ^/_detail/(.*) /lib/exe/detail.php?media=$1 last;
        rewrite ^/_export/([^/]+)/(.*) /doku.php?do=export_$1&id=$2 last;
        rewrite ^/(.*)         /doku.php?id=$1&$args last;
    }

    # Static library files
    location ~ ^/lib.*\.(js|css|gif|png|ico|jpg|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # PHP handling (only specific scripts)
    location ~ ^/(doku|lib/exe/(fetch|detail|indexer|js|css))\.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
    }

    # Block all other PHP
    location ~ \.php$ {
        return 404;
    }
}
```

---

## URL Rewriting Configuration

In DokuWiki's `conf/local.php`:

```php
$conf['userewrite'] = 1;
$conf['useslash'] = 1;
```

---

## Security Hardening

### Block Install Script

After installation, block the installer:

```nginx
location = /install.php { deny all; }
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=dw_login:10m rate=1r/s;

# Rate limit login attempts
location = /doku.php {
    if ($arg_do = "login") {
        limit_req zone=dw_login burst=5 nodelay;
    }
    
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

---

## ACL Configuration

DokuWiki's ACL should be configured in the admin panel or `conf/acl.auth.php`:

```
# namespace:page    @group    permission
*                   @ALL      0    # deny anonymous by default
*                   @user     8    # allow registered users to edit
wiki:*              @admin    16   # allow admin full access
```

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [MediaWiki Configuration](mediawiki.md)
