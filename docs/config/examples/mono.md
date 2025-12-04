---
title: Mono (.NET) FastCGI
description: Running .NET/ASP.NET websites with Mono behind NGINX.
---

# Mono (.NET) FastCGI

Run .NET websites behind NGINX using Mono's FastCGI server.

## Configuration

```nginx
server {
    server_name example.com;
    root /var/www/webapp;
    index index.html index.htm index.aspx default.aspx;

    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    location / {
        try_files $uri $uri/ /index.aspx;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires max;
        log_not_found off;
    }

    # ASP.NET files
    location ~ \.(aspx|asmx|ashx|asax|ascx|soap|rem|axd|cs|config|dll)$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

## Starting Mono FastCGI

### TCP Socket

```bash
fastcgi-mono-server2 /socket=tcp:9000
```

### Unix Socket (Recommended)

```bash
fastcgi-mono-server2 /socket=unix:/tmp/fastcgi.socket
```

Update NGINX config:

```nginx
fastcgi_pass unix:/tmp/fastcgi.socket;
```


