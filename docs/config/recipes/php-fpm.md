---
title: PHP-FPM
description: Modern NGINX configuration with PHP FastCGI Process Manager.
---

# PHP-FPM

Production configuration for NGINX with PHP-FPM (FastCGI Process Manager).

!!! warning "Security First"
    Many online guides contain security issues or don't handle `PATH_INFO` correctly. This guide addresses both concerns.

---

## Quick Start

### Basic Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        # Prevent execution of non-existent PHP files
        try_files $uri =404;

        # FastCGI settings
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;

        # Required parameters
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;

        # Security: block httpoxy attacks
        fastcgi_param HTTP_PROXY "";
    }

    # Block access to hidden files
    location ~ /\. {
        deny all;
    }
}
```

---

## Connection Methods

### Unix Socket (Recommended)

Lower latency for local connections:

```nginx
fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
```

PHP-FPM pool config (`/etc/php/8.2/fpm/pool.d/www.conf`):
```ini
listen = /var/run/php/php8.2-fpm.sock
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
```

### TCP Socket

For remote PHP-FPM servers or containers:

```nginx
fastcgi_pass 127.0.0.1:9000;
```

PHP-FPM pool config:
```ini
listen = 127.0.0.1:9000
```

### Upstream Pool

For load balancing across multiple PHP-FPM servers:

```nginx
upstream php {
    least_conn;
    server unix:/var/run/php/php8.2-fpm.sock weight=5;
    server 10.0.0.2:9000 backup;
    keepalive 16;
}

server {
    location ~ \.php$ {
        fastcgi_pass php;
        fastcgi_keep_conn on;
        # ... other params
    }
}
```

---

## FastCGI Parameters

Create `/etc/nginx/fastcgi_params` or `/etc/nginx/snippets/fastcgi-php.conf`:

```nginx
# Core parameters
fastcgi_param QUERY_STRING       $query_string;
fastcgi_param REQUEST_METHOD     $request_method;
fastcgi_param CONTENT_TYPE       $content_type;
fastcgi_param CONTENT_LENGTH     $content_length;

# Script paths
fastcgi_param SCRIPT_FILENAME    $document_root$fastcgi_script_name;
fastcgi_param SCRIPT_NAME        $fastcgi_script_name;
fastcgi_param PATH_INFO          $fastcgi_path_info;
fastcgi_param PATH_TRANSLATED    $document_root$fastcgi_path_info;
fastcgi_param REQUEST_URI        $request_uri;
fastcgi_param DOCUMENT_URI       $document_uri;
fastcgi_param DOCUMENT_ROOT      $document_root;
fastcgi_param SERVER_PROTOCOL    $server_protocol;

# Server info
fastcgi_param GATEWAY_INTERFACE  CGI/1.1;
fastcgi_param SERVER_SOFTWARE    nginx/$nginx_version;
fastcgi_param REMOTE_ADDR        $remote_addr;
fastcgi_param REMOTE_PORT        $remote_port;
fastcgi_param SERVER_ADDR        $server_addr;
fastcgi_param SERVER_PORT        $server_port;
fastcgi_param SERVER_NAME        $server_name;

# HTTPS detection
fastcgi_param HTTPS              $https if_not_empty;
fastcgi_param REDIRECT_STATUS    200;

# Security
fastcgi_param HTTP_PROXY         "";
```

---

## PATH_INFO Handling

For frameworks using `PATH_INFO` (e.g., `/index.php/controller/action`):

```nginx
location ~ [^/]\.php(/|$) {
    # Split PATH_INFO from script name
    fastcgi_split_path_info ^(.+?\.php)(/.*)$;

    # Verify script exists
    try_files $fastcgi_script_name =404;

    # Set PATH_INFO
    set $path_info $fastcgi_path_info;
    fastcgi_param PATH_INFO $path_info;

    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    fastcgi_index index.php;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

### Testing PATH_INFO

Create `test.php`:

```php
<?php
echo "SCRIPT_NAME: " . $_SERVER['SCRIPT_NAME'] . "\n";
echo "PATH_INFO: " . ($_SERVER['PATH_INFO'] ?? 'not set') . "\n";
echo "REQUEST_URI: " . $_SERVER['REQUEST_URI'] . "\n";
```

Test with: `curl http://localhost/test.php/foo/bar?v=1`

Expected output:
```
SCRIPT_NAME: /test.php
PATH_INFO: /foo/bar
REQUEST_URI: /test.php/foo/bar?v=1
```

---

## Performance Tuning

### Buffer Settings

```nginx
location ~ \.php$ {
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;

    # Buffers
    fastcgi_buffer_size 32k;
    fastcgi_buffers 16 16k;
    fastcgi_busy_buffers_size 32k;

    # Timeouts
    fastcgi_connect_timeout 60;
    fastcgi_send_timeout 180;
    fastcgi_read_timeout 180;

    # Keep connections alive
    fastcgi_keep_conn on;
}
```

### PHP-FPM Pool Tuning

`/etc/php/8.2/fpm/pool.d/www.conf`:

```ini
; Process manager
pm = dynamic
pm.max_children = 50
pm.start_servers = 10
pm.min_spare_servers = 5
pm.max_spare_servers = 20
pm.max_requests = 500

; Timeouts
request_terminate_timeout = 180

; Status page (optional)
pm.status_path = /fpm-status
ping.path = /fpm-ping
```

### Enable Status Page

```nginx
location ~ ^/(fpm-status|fpm-ping)$ {
    access_log off;
    allow 127.0.0.1;
    allow ::1;
    deny all;
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

---

## Security

### Block PHP in Uploads

```nginx
# Block PHP execution in upload directories
location ~* /(?:uploads|files|media)/.*\.php$ {
    deny all;
}
```

### Limit PHP Locations

Only allow PHP in specific directories:

```nginx
# Block PHP everywhere except allowed paths
location ~ \.php$ {
    return 403;
}

# Allow PHP in root and specific paths only
location ~ ^/(?:index|api|admin)\.php$ {
    fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
}
```

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=php:10m rate=10r/s;

location ~ \.php$ {
    limit_req zone=php burst=20 nodelay;
    # ... fastcgi config
}
```

---

## FastCGI Caching

```nginx
# Define cache zone (http block)
fastcgi_cache_path /var/cache/nginx/fastcgi
    levels=1:2
    keys_zone=php_cache:100m
    inactive=60m
    max_size=1g;

server {
    set $no_cache 0;

    # Don't cache POST requests
    if ($request_method = POST) { set $no_cache 1; }

    # Don't cache authenticated users
    if ($http_cookie ~* "session_id") { set $no_cache 1; }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;

        # Caching
        fastcgi_cache php_cache;
        fastcgi_cache_valid 200 10m;
        fastcgi_cache_bypass $no_cache;
        fastcgi_no_cache $no_cache;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | PHP-FPM not running, wrong socket path, or permission denied |
| 504 Gateway Timeout | Increase `fastcgi_read_timeout` and PHP's `max_execution_time` |
| File not found | Check `SCRIPT_FILENAME` parameter and `root` directive |
| Blank page | Check PHP error logs, ensure `display_errors = On` in development |
| Permission denied | Socket permissions - ensure NGINX user can access the socket |

### Debug 502 Errors

```bash
# Check PHP-FPM is running
systemctl status php8.2-fpm

# Check socket exists
ls -la /var/run/php/php8.2-fpm.sock

# Check NGINX error log
tail -f /var/log/nginx/error.log

# Check PHP-FPM log
tail -f /var/log/php8.2-fpm.log
```

### Socket Permissions

Ensure NGINX and PHP-FPM use the same user/group:

```ini
; PHP-FPM pool config
user = www-data
group = www-data
listen.owner = www-data
listen.group = www-data
```

---

## See Also

- [WordPress Configuration](wordpress.md)
- [Drupal Configuration](drupal.md)
- [Symfony Configuration](symfony.md)
- [FastCGI Examples](../examples/fastcgi.md)
