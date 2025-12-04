---
title: SSL/TLS Configuration
description: Modern SSL/TLS configuration for NGINX with best practices.
---

# SSL/TLS Configuration

Production-ready SSL/TLS configuration for NGINX following current best practices.

---

## Quick Start (Let's Encrypt)

### Certbot Installation

=== "Debian/Ubuntu"
    ```bash
    apt install certbot python3-certbot-nginx
    ```

=== "RHEL/CentOS"
    ```bash
    dnf install certbot python3-certbot-nginx
    ```

### Obtain Certificate

```bash
certbot --nginx -d example.com -d www.example.com
```

---

## Modern SSL Configuration

### Recommended Settings (2024)

```nginx
server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com;

    # Certificate files
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL session settings
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern protocols only (TLS 1.2 and 1.3)
    ssl_protocols TLSv1.2 TLSv1.3;

    # Modern cipher suites
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
    resolver 1.1.1.1 8.8.8.8 valid=300s;
    resolver_timeout 5s;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ... rest of server config
}
```

---

## HTTP to HTTPS Redirect

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

---

## DH Parameters

Generate strong Diffie-Hellman parameters:

```bash
openssl dhparam -out /etc/nginx/dhparam.pem 2048
```

Add to server block:

```nginx
ssl_dhparam /etc/nginx/dhparam.pem;
```

---

## Certificate Profiles

### Modern (TLS 1.3 Only)

For clients that support TLS 1.3:

```nginx
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;
```

### Intermediate (Recommended)

Balance between security and compatibility:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
```

### Legacy (Old Clients)

Only if you need IE11/Windows 7 support:

```nginx
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA;
ssl_prefer_server_ciphers on;
```

!!! warning
    Legacy configuration includes weak ciphers. Only use if absolutely necessary.

---

## Wildcard Certificates

For multiple subdomains:

```bash
certbot certonly --manual --preferred-challenges dns \
    -d example.com -d *.example.com
```

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name *.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
}
```

---

## Multi-Domain (SAN) Certificates

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com www.example.com api.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
}
```

---

## Client Certificate Authentication

For mutual TLS (mTLS):

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name secure.example.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # Client certificate verification
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location / {
        # Pass client cert info to backend
        proxy_set_header X-SSL-Client-Cert $ssl_client_cert;
        proxy_set_header X-SSL-Client-S-DN $ssl_client_s_dn;
        proxy_pass http://backend;
    }
}
```

---

## SSL Termination for Backends

```nginx
upstream backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.com.crt;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Auto-Renewal

### Certbot Timer

Certbot installs a systemd timer automatically. Verify:

```bash
systemctl status certbot.timer
```

### Manual Cron

```bash
# /etc/cron.d/certbot
0 0,12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
```

---

## Testing SSL Configuration

### SSL Labs Test

```bash
# Check your grade
curl -s "https://api.ssllabs.com/api/v3/analyze?host=example.com" | jq '.endpoints[0].grade'
```

### OpenSSL Test

```bash
# Test connection
openssl s_client -connect example.com:443 -servername example.com

# Check certificate
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates
```

### NGINX Test

```bash
nginx -t
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Certificate not trusted | Ensure full chain is included |
| Mixed content warnings | Use `X-Forwarded-Proto` header |
| OCSP stapling fails | Check resolver is set |
| Slow SSL handshake | Enable session cache |
| ERR_SSL_VERSION_OR_CIPHER_MISMATCH | Client doesn't support configured protocols |

---

## Reusable SSL Snippet

Create `/etc/nginx/snippets/ssl.conf`:

```nginx
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 8.8.8.8 valid=300s;
resolver_timeout 5s;

add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

Use in server blocks:

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    include snippets/ssl.conf;

    # ... rest of config
}
```

---

## See Also

- [Security Hardening](security.md)
- [HTTP/3 (QUIC) Configuration](http3.md)

