---
title: IMAP/POP3 Proxy
description: Example NGINX configurations for IMAP and POP3 mail proxying.
---

# IMAP/POP3 Proxy

NGINX can proxy IMAP and POP3 mail protocols.

!!! note "Build Requirements"
    You need to compile NGINX with mail support:
    ```bash
    ./configure --with-mail --with-mail_ssl_module
    ```
    Use `--without-http` if you don't need HTTP proxying.

---

## Basic IMAP Proxy

```nginx
mail {
    auth_http localhost:9000/cgi-bin/auth;
    # Or use Unix socket:
    # auth_http unix:/path/socket:/cgi-bin/auth;

    proxy on;

    imap_capabilities "IMAP4rev1" "UIDPLUS";

    server {
        listen 143;
        protocol imap;
    }

    # POP3 proxy (uncomment to enable)
    # pop3_capabilities "TOP" "USER";
    # server {
    #     listen 110;
    #     protocol pop3;
    # }
}
```

---

## IMAP Proxy with STARTTLS

```nginx
mail {
    auth_http localhost:9000/cgi-bin/auth;

    proxy on;
    starttls on;  # Enable STARTTLS for all mail servers

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:MAILSSL:16m;
    ssl_session_timeout 1d;
    ssl_certificate /etc/nginx/ssl/mail.example.org.crt;
    ssl_certificate_key /etc/nginx/ssl/mail.example.org.key;

    imap_capabilities "IMAP4rev1" "UIDPLUS";

    server {
        listen 143;
        protocol imap;
        server_name mx.example.org;
    }

    # POP3 with STARTTLS (uncomment to enable)
    # pop3_capabilities "TOP" "USER";
    # server {
    #     listen 110;
    #     protocol pop3;
    # }
}
```

## IMAPS (Port 993)

For implicit TLS on port 993:

```nginx
mail {
    auth_http localhost:9000/cgi-bin/auth;
    proxy on;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_certificate /etc/nginx/ssl/mail.example.org.crt;
    ssl_certificate_key /etc/nginx/ssl/mail.example.org.key;

    server {
        listen 993 ssl;
        protocol imap;
    }

    server {
        listen 995 ssl;
        protocol pop3;
    }
}
```

---

## Authentication Backend

The `auth_http` directive points to an authentication script that returns the backend mail server.
