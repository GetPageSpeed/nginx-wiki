---
title: PHP on Windows
description: Running PHP FastCGI with NGINX on Windows.
---

# PHP FastCGI on Windows

## Overview

NGINX interfaces with PHP via `php-cgi.exe` on Windows. While Windows is not the recommended platform for production NGINX deployments, this guide covers the setup for development purposes.

## Prerequisites

1. NGINX for Windows
2. PHP for Windows
3. Ensure `php-cgi.exe` is in your PHP installation directory

## Quick Start

### Start PHP FastCGI

Create `start-php-fcgi.bat`:

```batch
@ECHO OFF
ECHO Starting PHP FastCGI...
set PATH=C:\PHP;%PATH%
C:\PHP\php-cgi.exe -b 127.0.0.1:9000
```

!!! tip "Running in Background"
    To run PHP-CGI hidden, use Windows Task Scheduler or a service wrapper like NSSM (Non-Sucking Service Manager).

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name localhost;
    root C:/www;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        include fastcgi_params;
    }
}
```

## Running as Windows Service

### Using NSSM

1. Download NSSM from nssm.cc
2. Install PHP-CGI as a service:

```batch
nssm install php-cgi "C:\PHP\php-cgi.exe" -b 127.0.0.1:9000
nssm start php-cgi
```

3. Install NGINX as a service:

```batch
nssm install nginx "C:\nginx\nginx.exe"
nssm set nginx AppDirectory "C:\nginx"
nssm start nginx
```

### Using Task Scheduler

1. Open Task Scheduler
2. Create a task to run at startup under SYSTEM account
3. Action: Start program `C:\PHP\php-cgi.exe`
4. Arguments: `-b 127.0.0.1:9000`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | PHP-CGI not running or wrong port |
| "No input file specified" | Check `SCRIPT_FILENAME` path uses forward slashes |
| PHP crashes | Increase `PHP_FCGI_MAX_REQUESTS` environment variable |

## Recommendation

!!! warning "Production Use"
    For production PHP workloads, Linux with PHP-FPM is strongly recommended over Windows. Consider using WSL2 for development if you need Windows.

## See Also

- [PHP-FPM Configuration](../recipes/php-fpm.md) (Linux)
