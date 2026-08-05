---
title: NGINX FAQ - Frequently Asked Questions and Answers
description: Common NGINX questions answered including pronunciation, htpasswd generation, load balancing, proxying, and troubleshooting.
keywords: nginx faq, nginx questions, nginx pronunciation, nginx htpasswd, nginx load balancing, nginx proxy, nginx help
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: WebPage
tags:
  - community
  - faq
  - troubleshooting
  - help
  - questions
---

# Frequently Asked Questions

## General

### How do you pronounce "NGINX"?

**Correct:** "engine-X" (en-juhn-eks)

**Incorrect:** "en-jinks"

### Is it safe to use the development branch?

Generally, yes. Development releases are stable; many users run them in production. The main concern is that third-party module APIs may change.

**Best practice:** Wait 2-3 days after a development release. If no emergency fixes are released, it's likely stable.

### How do I generate `.htpasswd` without Apache tools?

Using OpenSSL:

```bash
# Crypt encryption
printf "John:$(openssl passwd -crypt V3Ry)\n" >> .htpasswd

# Apache MD5 (apr1)
printf "Mary:$(openssl passwd -apr1 SEcRe7)\n" >> .htpasswd

# MD5
printf "Jane:$(openssl passwd -1 V3RySEcRe7)\n" >> .htpasswd
```

Or use Python's `htpasswd.py` script.

### Why isn't my configuration working?

1. Enable [debug logging](../config/debugging.md)
2. Review error log **line by line**
3. Search online for similar issues
4. Ask on IRC or mailing list with full details

## HTTP

### What does `@location` mean?

`@location` is a **named location**. It preserves `$uri` and can only be reached via:
- `error_page`
- `post_action`
- `try_files`

Example:

```nginx
location / {
    try_files $uri $uri/ @backend;
}

location @backend {
    proxy_pass http://backend;
}
```

## Proxying

### NGINX vs Squid?

- **NGINX**: Reverse proxy, minimal RAM/CPU under load
- **Squid**: Caching proxy for dynamic content

NGINX's proxy module supports caching upstream servers.

### How do I show upload progress?

Use the [Upload Progress module](../ecosystem/3rd-party-modules.md).

## Load Balancing

### What algorithms does NGINX support?

- Round-robin (default)
- Least connections (`least_conn`)
- IP hash (`ip_hash`)
- All support weights

## Mail

### How do I configure IMAP proxy?

See [IMAP Proxy Example](../config/examples/imap-proxy.md) and [IMAP Auth with PHP](../config/examples/imap-auth-php.md).

### How do I use NGINX as SMTP proxy with Postfix?

```nginx
mail {
    server_name mail.example.com;
    auth_http localhost:8008/auth-smtppass.php;

    server {
        listen 25;
        protocol smtp;
        timeout 5s;
        proxy on;
        xclient off;
        smtp_auth none;
    }
}
```

## Miscellaneous

### Why do I see "Welcome to nginx!" on Facebook/Google?

NGINX is not a virus. This usually indicates a misconfigured proxy or DNS hijacking. Check your network settings and DNS configuration.

### Is chroot supported?

Not built-in. Use OS-level isolation (BSD Jails, Docker, OpenVZ).

### What about mod_suexec?

NGINX doesn't need it. Run separate NGINX instances per user, or use FastCGI with per-user PHP-FPM pools.


