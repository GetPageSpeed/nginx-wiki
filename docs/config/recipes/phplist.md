---
title: PHPList
description: A sample NGINX configuration for PHPList newsletter manager.
---

# PHPList

PHPList is an open-source newsletter and email marketing software.

---

## Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    root /var/www/phplist/public_html/lists;
    index index.php;

    access_log /var/log/nginx/phplist_access.log;
    error_log /var/log/nginx/phplist_error.log;

    charset utf-8;

    # Block log and config files
    location ~* \.(txt|log|inc)$ {
        allow 127.0.0.1;
        deny all;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires max;
        log_not_found off;
    }

    # Block config directory
    location /config {
        deny all;
    }

    # Only allow specific public PHP files
    location ~* (index\.php|upload\.php|connector\.php|dl\.php|ut\.php|lt\.php|download\.php)$ {
        fastcgi_split_path_info ^(.|\.php)(/.+)$;
        include /etc/nginx/fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors on;
        fastcgi_pass 127.0.0.1:9000;
    }

    # Block all other PHP files
    location ~ \.php$ {
        deny all;
    }
}
```

---

## Security

This configuration follows PHPList's `.htaccess` rules:

- Only whitelisted PHP files are accessible
- Config directory is blocked
- Log files are only accessible from localhost

