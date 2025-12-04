---
title: SPIP
description: A sample NGINX configuration for SPIP CMS.
---

# SPIP

## Configuration

```nginx
server {
    server_name example.com;
    client_max_body_size 10m;
    root /var/www/spip;
    index index.php;

    location / {
        try_files $uri $uri/ /spip.php?$args;
    }

    # Block access to sensitive directories
    location ~^/(tmp|config)/ {
        return 403;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

!!! warning "Security"
    SPIP was designed for Apache. Block `/tmp` and `/config` directories as database dumps in `/tmp` could expose admin passwords.

    Alternative: Move these directories outside the web root and redefine `_DIR_TMP` and `_DIR_CONNECT` in `mes_options.php`.

!!! note "Buffer Size"
    The `fastcgi_buffers` settings prevent "upstream sent too big header" errors.


