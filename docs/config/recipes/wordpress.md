---
title: NGINX WordPress Configuration - Performance Tuning & Security Hardening
description: Production-ready NGINX configuration for WordPress. Includes PHP-FPM setup, WP Super Cache, W3 Total Cache, security hardening, permalinks, multisite, and performance optimization.
keywords: nginx wordpress, wordpress nginx configuration, nginx php-fpm wordpress, wordpress nginx security, wordpress nginx performance, nginx wp-admin, nginx wordpress multisite, wordpress nginx cache
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - wordpress
  - php-fpm
  - recipe
  - caching
  - security
---

# WordPress

Production-ready NGINX configuration for WordPress with security hardening, caching, and performance optimization.

---

## Quick Start

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com www.example.com;

    root /var/www/wordpress;
    index index.php;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/wordpress.access.log;
    error_log /var/log/nginx/wordpress.error.log;

    # Favicon and robots
    location = /favicon.ico { log_not_found off; access_log off; }
    location = /robots.txt  { log_not_found off; access_log off; allow all; }

    # Block access to hidden files
    location ~ /\. { deny all; }

    # Block access to sensitive files
    location ~* ^/(wp-config\.php|readme\.html|license\.txt)$ { deny all; }

    # Block PHP in uploads
    location ~* /(?:uploads|files)/.*\.php$ { deny all; }

    # WordPress permalinks
    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    # PHP handling
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param HTTP_PROXY "";
        fastcgi_read_timeout 300;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
    }

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        log_not_found off;
        access_log off;
    }
}
```

---

## Security Hardening

### Block XML-RPC Attacks

XML-RPC is frequently targeted for brute-force attacks. Disable if not needed:

```nginx
location = /xmlrpc.php {
    deny all;
    access_log off;
    log_not_found off;
}
```

Or restrict to specific IPs (e.g., Jetpack):

```nginx
location = /xmlrpc.php {
    allow 122.248.245.244/32;  # Jetpack
    allow 54.217.201.243/32;
    deny all;
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

### Protect wp-admin

```nginx
# Rate limit login attempts
limit_req_zone $binary_remote_addr zone=wp_login:10m rate=1r/s;

location = /wp-login.php {
    limit_req zone=wp_login burst=3 nodelay;
    
    # Optional: IP whitelist
    # allow 192.168.1.0/24;
    # deny all;
    
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}

# Block wp-admin for non-logged-in users (optional, breaks some plugins)
# location ~* /wp-admin/(?!admin-ajax\.php) {
#     auth_basic "Restricted";
#     auth_basic_user_file /etc/nginx/.htpasswd;
# }
```

### Block File Uploads Execution

```nginx
# Block PHP execution in uploads
location ~* /wp-content/uploads/.*\.php$ {
    deny all;
}

# Block PHP execution in plugins/themes upload directories
location ~* /wp-content/(?:plugins|themes)/.*\.php$ {
    # Allow legitimate files
    location ~* /wp-content/(?:plugins|themes)/[^/]+/[^/]+\.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
    deny all;
}
```

---

## FastCGI Caching

Enable full-page caching for dramatic performance gains:

```nginx
# Define cache zone (in http block)
fastcgi_cache_path /var/cache/nginx/wordpress
    levels=1:2
    keys_zone=wordpress:100m
    inactive=60m
    max_size=1g;

fastcgi_cache_key "$scheme$request_method$host$request_uri";

server {
    # ... SSL and other config ...

    set $skip_cache 0;

    # Don't cache POST requests
    if ($request_method = POST) { set $skip_cache 1; }

    # Don't cache URLs with query strings
    if ($query_string != "") { set $skip_cache 1; }

    # Don't cache admin, login, or specific pages
    if ($request_uri ~* "/wp-admin/|/xmlrpc.php|wp-.*.php|^/feed/*|/tag/.*/feed/*|index.php|sitemap(_index)?.xml") {
        set $skip_cache 1;
    }

    # Don't cache for logged-in users or recent commenters
    if ($http_cookie ~* "comment_author|wordpress_[a-f0-9]+|wp-postpass|wordpress_no_cache|wordpress_logged_in") {
        set $skip_cache 1;
    }

    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";

        # Caching
        fastcgi_cache wordpress;
        fastcgi_cache_valid 200 60m;
        fastcgi_cache_bypass $skip_cache;
        fastcgi_no_cache $skip_cache;
        add_header X-FastCGI-Cache $upstream_cache_status;
    }
}
```

### Cache Purging

Install `ngx_cache_purge` module for automatic cache invalidation:

```nginx
location ~ /purge(/.*) {
    allow 127.0.0.1;
    deny all;
    fastcgi_cache_purge wordpress "$scheme$request_method$host$1";
}
```

---

## Multisite: Subdirectories

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;
    root /var/www/wordpress;
    index index.php;

    # ... SSL config ...

    # Multisite subdirectory handling
    if (!-e $request_filename) {
        rewrite /wp-admin$ $scheme://$host$uri/ permanent;
        rewrite ^(/[^/]+)?(/wp-.*) $2 last;
        rewrite ^(/[^/]+)?(/.*\.php) $2 last;
    }

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    # Handle ms-files.php for older multisite
    location ~ ^/files/(.*)$ {
        try_files /wp-content/blogs.dir/$blogid/$uri /wp-includes/ms-files.php?file=$1;
        expires max;
        log_not_found off;
    }

    location ^~ /blogs.dir {
        internal;
        alias /var/www/wordpress/wp-content/blogs.dir;
    }

    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

---

## Multisite: Subdomains

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com *.example.com;
    root /var/www/wordpress;
    index index.php;

    # ... SSL config (use wildcard cert) ...

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ ^/files/(.*)$ {
        try_files /wp-content/blogs.dir/$blogid/$uri /wp-includes/ms-files.php?file=$1;
        expires max;
        log_not_found off;
    }

    location ^~ /blogs.dir {
        internal;
        alias /var/www/wordpress/wp-content/blogs.dir;
    }

    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

---

## WordPress in Subdirectory

```nginx
location /blog {
    alias /var/www/wordpress;
    index index.php;

    location ~ \.php$ {
        fastcgi_split_path_info ^(/blog)(/.*)$;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $request_filename;
    }

    location ~ /blog/(.+) {
        try_files $uri $uri/ /blog/index.php?$args;
    }
}
```

---

## Performance Tuning

### Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json application/javascript 
           application/rss+xml application/atom+xml image/svg+xml;
```

### Brotli Compression (Better)

```nginx
# Requires ngx_brotli module
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css text/xml application/json application/javascript
             application/rss+xml application/atom+xml image/svg+xml;
```

### Client-Side Caching

```nginx
# Aggressive caching for versioned assets
location ~* \.(js|css)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Images
location ~* \.(png|jpg|jpeg|gif|ico|svg|webp)$ {
    expires 1y;
    add_header Cache-Control "public";
}

# Fonts
location ~* \.(woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public";
    add_header Access-Control-Allow-Origin "*";
}
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| White screen of death | Check PHP-FPM logs, increase `memory_limit` |
| 502 Bad Gateway | PHP-FPM not running or wrong socket path |
| Slow admin | Increase `fastcgi_read_timeout` to 300+ |
| Broken permalinks | Ensure `try_files` includes `$args` |
| Mixed content (HTTPS) | Set `WP_HOME` and `WP_SITEURL` in wp-config.php |
| File upload fails | Increase `client_max_body_size` |

### Increase Upload Limit

```nginx
client_max_body_size 64M;
```

In `php.ini`:
```ini
upload_max_filesize = 64M
post_max_size = 64M
```

---

## See Also

- [PHP-FPM Configuration](php-fpm.md) - Detailed PHP-FPM setup
- [FastCGI Examples](../examples/fastcgi.md) - General FastCGI patterns
- [Server Blocks Examples](../examples/server-blocks.md) - Virtual host configuration
