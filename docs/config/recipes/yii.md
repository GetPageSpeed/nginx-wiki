---
title: Yii Framework
description: A sample NGINX configuration for Yii.
---

# Yii Framework

This configuration enables SEF (Search Engine Friendly) URLs for Yii applications.

## NGINX Configuration

```nginx
server {
    server_name domain.tld;
    root /usr/share/nginx/html;
    index index.html index.php;

    # SEF URLs for your Yii app
    location /sampleapp {
        rewrite ^/sampleapp/(.*)$ /sampleapp/index.php?r=$1;
    }

    # Block access to protected directories
    location ~ /(protected|framework|nbproject) {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ /themes/\w+/views {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Static files
    location ~ \.(js|css|png|jpg|gif|swf|ico|pdf|mov|fla|zip|rar)$ {
        try_files $uri =404;
    }

    location ~ \.php$ {
        root /usr/share/nginx/html;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /usr/share/nginx/html/$fastcgi_script_name;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
    }
}
```

## Yii Configuration

In your `main.php` config file, enable URL path format:

```php
'urlManager' => array(
    'urlFormat' => 'path',
    'showScriptName' => false,
    'rules' => array(
        '<controller:\w+>/<id:\d+>' => '<controller>/view',
        '<controller:\w+>/<action:\w+>/<id:\d+>' => '<controller>/<action>',
        '<controller:\w+>/<action:\w+>' => '<controller>/<action>',
    ),
)
```


