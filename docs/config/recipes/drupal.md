---
title: NGINX Drupal Configuration Guide
description: Production-ready NGINX configuration for Drupal 9 and 10 with security hardening, multisite setup, and performance optimization.
keywords: nginx, drupal, drupal 10, drupal 9, cms, php, fastcgi, multisite, security, caching
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - drupal
  - cms
  - php
  - security
  - multisite
---

# Drupal

Production-ready NGINX configuration for Drupal 9 and 10 with security hardening and performance optimization.

---

## Quick Start (Drupal 10)

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com www.example.com;

    root /var/www/drupal/web;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/drupal.access.log;
    error_log /var/log/nginx/drupal.error.log;

    # Favicon and robots
    location = /favicon.ico { log_not_found off; access_log off; }
    location = /robots.txt  { log_not_found off; access_log off; allow all; }

    # Block access to hidden files (except .well-known)
    location ~ (^|/)\. {
        return 403;
    }
    location ^~ /.well-known/ {
        allow all;
    }

    # Block access to sensitive files
    location ~* \.(engine|inc|install|make|module|profile|po|sh|.*sql|theme|twig|tpl(\.php)?|xtmpl|yml)(~|\.sw[op]|\.bak|\.orig|\.save)?$|^/(\.(?!well-known).*|Entries.*|Repository|Root|Tag|Template|composer\.(json|lock)|web\.config)$|^#.*#$|\.php(~|\.sw[op]|\.bak|\.orig|\.save)$ {
        deny all;
        return 404;
    }

    # Block text/log files access
    location ~* \.(txt|log)$ {
        allow 127.0.0.1;
        deny all;
    }

    # Block PHP in wrong locations
    location ~ \..*/.*\.php$ { return 403; }
    location ~ ^/sites/.*/private/ { return 403; }
    location ~ ^/sites/[^/]+/files/.*\.php$ { deny all; }
    location ~ /vendor/.*\.php$ { deny all; return 404; }

    # Main location
    location / {
        try_files $uri /index.php?$query_string;
    }

    # PHP handling
    location ~ '\.php$|^/update.php' {
        fastcgi_split_path_info ^(.+?\.php)(|/.*)$;
        try_files $fastcgi_script_name =404;

        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param QUERY_STRING $query_string;
        fastcgi_intercept_errors on;

        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_read_timeout 300;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf|eot)$ {
        try_files $uri @rewrite;
        expires 1y;
        add_header Cache-Control "public, immutable";
        log_not_found off;
        access_log off;
    }

    # Image styles
    location ~ ^/sites/.*/files/styles/ {
        try_files $uri @rewrite;
    }

    # Private files
    location ~ ^(/[a-z\-]+)?/system/files/ {
        try_files $uri /index.php?$query_string;
    }

    location @rewrite {
        rewrite ^ /index.php;
    }

    # Enforce clean URLs
    if ($request_uri ~* "^(.*/)index\.php/(.*)") {
        return 307 $1$2;
    }
}
```

---

## Security Hardening

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=drupal:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=drupal_login:10m rate=1r/s;

server {
    # General rate limit
    limit_req zone=drupal burst=20 nodelay;

    # Strict limit on login
    location = /user/login {
        limit_req zone=drupal_login burst=3 nodelay;
        try_files $uri /index.php?$query_string;
    }

    location = /user/register {
        limit_req zone=drupal_login burst=3 nodelay;
        try_files $uri /index.php?$query_string;
    }
}
```

### Block Common Attacks

```nginx
# Block suspicious query strings
if ($query_string ~* "(base64_encode|base64_decode|eval\(|union.*select|script>|<script)") {
    return 403;
}

# Block suspicious user agents
if ($http_user_agent ~* "(nikto|sqlmap|libwww|python-urllib)") {
    return 403;
}
```

### Admin Protection

```nginx
# Optional: IP restrict admin paths
location ~* ^/admin {
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    deny all;
    try_files $uri /index.php?$query_string;
}
```

---

## Drupal Multisite

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name site1.example.com site2.example.com site3.example.com;

    root /var/www/drupal/web;
    index index.php;

    # SSL (wildcard or multi-domain cert)
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Map domain to sites directory
    set $site_dir default;
    if ($host = "site1.example.com") { set $site_dir site1; }
    if ($host = "site2.example.com") { set $site_dir site2; }

    location / {
        try_files $uri /index.php?$query_string;
    }

    location ~ '\.php$|^/update.php' {
        fastcgi_split_path_info ^(.+?\.php)(|/.*)$;
        try_files $fastcgi_script_name =404;

        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    }
}
```

---

## Performance Optimization

### FastCGI Caching

```nginx
fastcgi_cache_path /var/cache/nginx/drupal
    levels=1:2
    keys_zone=drupal:100m
    inactive=60m
    max_size=2g;

server {
    set $skip_cache 0;

    # Don't cache POST or authenticated requests
    if ($request_method = POST) { set $skip_cache 1; }
    if ($http_cookie ~* "SESS[a-f0-9]+|SSESS[a-f0-9]+") { set $skip_cache 1; }

    # Don't cache admin or user paths
    if ($request_uri ~* "^/admin|^/user|^/batch") { set $skip_cache 1; }

    location ~ '\.php$|^/update.php' {
        fastcgi_split_path_info ^(.+?\.php)(|/.*)$;
        try_files $fastcgi_script_name =404;

        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;

        # Caching
        fastcgi_cache drupal;
        fastcgi_cache_valid 200 30m;
        fastcgi_cache_bypass $skip_cache;
        fastcgi_no_cache $skip_cache;
        add_header X-Cache $upstream_cache_status;
    }
}
```

### Gzip/Brotli

```nginx
# Gzip
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json application/javascript
           application/rss+xml application/atom+xml image/svg+xml;

# Brotli (requires module)
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css text/xml application/json application/javascript
             application/rss+xml application/atom+xml image/svg+xml;
```

---

## Drush Commands

Useful Drush commands for NGINX + Drupal:

```bash
# Clear all caches
drush cr

# Put site in maintenance mode
drush state:set system.maintenance_mode 1 --input-format=integer

# Take out of maintenance mode
drush state:set system.maintenance_mode 0 --input-format=integer

# Update database
drush updatedb
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Clean URLs not working | Ensure `try_files` ends with `$query_string` |
| Private files 403 | Check `location ~ ^(/[a-z\-]+)?/system/files/` path |
| Image styles 404 | Add `location ~ ^/sites/.*/files/styles/` |
| 502 on update.php | Increase `fastcgi_read_timeout` to 300+ |
| Aggregated CSS/JS 404 | Ensure static files `try_files` includes `@rewrite` |

### Enable Drupal Logging

In `settings.php`:

```php
$config['system.logging']['error_level'] = 'verbose';
```

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [WordPress Configuration](wordpress.md)
- [FastCGI Examples](../examples/fastcgi.md)
