---
title: osTicket
description: A sample NGINX configuration for osTicket helpdesk.
---

# osTicket

osTicket is an open-source support ticket system.

---

## Configuration

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name tickets.example.com;
    return 301 https://tickets.example.com$request_uri;
}

server {
    listen 443 ssl;
    server_name tickets.example.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/cert.key;

    keepalive_timeout 70;
    root /var/www/osticket;
    index index.php index.html index.htm;

    set $path_info "";

    # Block include directory
    location ~ /include {
        deny all;
        return 403;
    }

    # API routing
    if ($request_uri ~ "^/api(/[^\?]+)") {
        set $path_info $1;
    }

    location ~ ^/api/(?:tickets|tasks).*$ {
        try_files $uri $uri/ /api/http.php?$query_string;
    }

    # SCP (Staff Control Panel) path info
    if ($request_uri ~ "^/scp/.*\.php(/[^\?]+)") {
        set $path_info $1;
    }

    if ($request_uri ~ "^/.*\.php(/[^\?]+)") {
        set $path_info $1;
    }

    # AJAX routing
    location ~ ^/scp/ajax.php/.*$ {
        try_files $uri $uri/ /scp/ajax.php?$query_string;
    }

    location ~ ^/ajax.php/.*$ {
        try_files $uri $uri/ /ajax.php?$query_string;
    }

    location / {
        try_files $uri $uri/ index.php;
    }

    location ~ \.php$ {
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param PATH_INFO $path_info;
        fastcgi_pass 127.0.0.1:8888;
    }
}
```

---

## Key Features

| Feature | Purpose |
|---------|---------|
| HTTPS redirect | All traffic forced to SSL |
| `$path_info` variable | Handles osTicket's PATH_INFO requirements |
| API routing | Routes `/api/tickets` and `/api/tasks` to `http.php` |
| AJAX support | Routes AJAX requests to `ajax.php` |

