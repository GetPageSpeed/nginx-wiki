---
title: MyBB
description: A sample NGINX configuration for MyBB forum software.
---

# MyBB

## Configuration

```nginx
server {
    server_name forum.example.com;
    access_log logs/forum.access;
    error_log logs/forum.error error;
    root /var/www/mybb;

    location / {
        index index.php;
    }

    # Deny access to internal files
    location ~ /(inc|uploads/avatars) {
        deny all;
    }

    # PHP handling
    location ~ \.php$ {
        fastcgi_pass unix:/tmp/php.socket;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }
}
```

!!! warning "Security Note"
    Set `cgi.fix_pathinfo=0` in php.ini to prevent the path info security vulnerability where uploaded files like `pic.gif/foo.php` could be executed as PHP.

See the [PHP-FPM guide](php-fpm.md) for details on setting up the PHP socket.
