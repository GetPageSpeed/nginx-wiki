---
title: CodeIgniter
description: NGINX configuration for CodeIgniter 3 and 4 PHP framework.
---

# CodeIgniter

Production-ready NGINX configuration for CodeIgniter 3 and 4.

---

## CodeIgniter 4

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    # CodeIgniter 4 public directory
    root /var/www/codeigniter/public;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Block hidden files
    location ~ /\. { deny all; }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Front controller
    location / {
        try_files $uri $uri/ /index.php$is_args$args;
    }

    # Only execute index.php
    location ~ ^/index\.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
        fastcgi_read_timeout 300;
    }

    # Block other PHP files
    location ~ \.php$ {
        return 404;
    }
}
```

### CodeIgniter 4 Configuration

In `app/Config/App.php`:

```php
public string $baseURL = 'https://example.com/';
public string $indexPage = '';
```

---

## CodeIgniter 3

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    root /var/www/codeigniter;
    index index.php;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Block sensitive directories
    location ^~ /application/ { deny all; }
    location ^~ /system/ { deny all; }

    # Block hidden files
    location ~ /\. { deny all; }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }

    # Front controller
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # Only execute index.php
    location = /index.php {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param HTTP_PROXY "";
    }

    # Block other PHP files
    location ~ \.php$ {
        return 404;
    }
}
```

### CodeIgniter 3 Configuration

In `application/config/config.php`:

```php
$config['base_url'] = 'https://example.com/';
$config['index_page'] = '';
$config['uri_protocol'] = 'REQUEST_URI';
```

---

## Security Notes

| Setting | Purpose |
|---------|---------|
| Block `/application/` | Prevents access to source code |
| Block `/system/` | Prevents access to framework core |
| Only allow `index.php` | Prevents execution of arbitrary PHP |

---

## See Also

- [PHP-FPM Configuration](php-fpm.md)
- [Symfony Configuration](symfony.md)
