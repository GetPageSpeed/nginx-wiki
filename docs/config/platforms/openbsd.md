---
title: NGINX on OpenBSD - Installation and Configuration Guide
description: Install NGINX on OpenBSD using packages or ports, configure rc.d services, and set up PF firewall rules with pledge/unveil support.
keywords: nginx openbsd, nginx bsd, nginx pkg_add, nginx rcctl, nginx pf firewall, openbsd web server
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - installation
  - openbsd
  - bsd
  - security
  - firewall
  - ports
---

# Installing NGINX on OpenBSD

OpenBSD includes NGINX in its ports and packages system, making installation straightforward.

## Using Packages (Recommended)

The easiest way to install NGINX on OpenBSD:

```bash
pkg_add nginx
```

This installs a pre-built NGINX with commonly needed modules.

### Enable and Start

```bash
# Enable at boot
rcctl enable nginx

# Start now
rcctl start nginx
```

### Configuration Location

- Main config: `/etc/nginx/nginx.conf`
- Document root: `/var/www/htdocs`
- Logs: `/var/log/nginx/`

---

## Using Ports

For custom builds with specific modules:

```bash
cd /usr/ports/www/nginx
make install clean
```

---

## Building from Source

### Install Dependencies

```bash
pkg_add pcre2
pkg_add gmake
```

### Download and Build

```bash
# Download latest stable
ftp https://nginx.org/download/nginx-1.26.2.tar.gz
tar xzf nginx-1.26.2.tar.gz
cd nginx-1.26.2

# Configure
./configure \
    --prefix=/usr/local \
    --sbin-path=/usr/local/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --pid-path=/var/run/nginx.pid \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --http-client-body-temp-path=/var/cache/nginx/client_temp \
    --http-proxy-temp-path=/var/cache/nginx/proxy_temp \
    --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
    --user=www \
    --group=www \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_gzip_static_module \
    --with-http_stub_status_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-pcre

# Build and install
gmake -j$(sysctl -n hw.ncpu)
doas gmake install

# Create cache directory
doas mkdir -p /var/cache/nginx
doas chown www:www /var/cache/nginx
```

---

## rc.d Service Script

If building from source, create `/etc/rc.d/nginx`:

```bash
#!/bin/ksh

daemon="/usr/local/sbin/nginx"

. /etc/rc.d/rc.subr

rc_reload=YES
rc_configtest=YES

rc_cmd $1
```

```bash
chmod 555 /etc/rc.d/nginx
```

---

## Managing NGINX

### Using rcctl (Recommended)

```bash
# Start
rcctl start nginx

# Stop
rcctl stop nginx

# Restart
rcctl restart nginx

# Reload configuration
rcctl reload nginx

# Check configuration
nginx -t

# Check status
rcctl check nginx
```

### Manual Signals

```bash
# Graceful shutdown
kill -QUIT $(cat /var/run/nginx.pid)

# Reload configuration
kill -HUP $(cat /var/run/nginx.pid)

# Reopen log files
kill -USR1 $(cat /var/run/nginx.pid)
```

---

## OpenBSD-Specific Notes

### Pledge and Unveil

OpenBSD's NGINX package is built with pledge(2) and unveil(2) support for enhanced security.

### chroot

Consider running NGINX in a chroot for additional isolation:

```bash
# In nginx.conf
# Paths are relative to chroot
# chroot /var/www;
```

### PF Firewall

Allow HTTP/HTTPS traffic:

```
# /etc/pf.conf
pass in on egress proto tcp from any to any port { 80 443 }
```

```bash
pfctl -f /etc/pf.conf
```

---

## See Also

- [OpenBSD FAQ - Package Management](https://www.openbsd.org/faq/faq15.html)
- [Building NGINX from Source](../../modules-dev/compiling.md)
