---
title: NGINX Configure Options - Complete Build Options Reference
description: Reference for NGINX ./configure script options. Set paths, enable modules, configure SSL, PCRE, zlib, and compiler flags for custom builds.
keywords: NGINX configure options, NGINX build options, ./configure NGINX, NGINX modules, NGINX compilation, NGINX source build
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - configure options
  - compilation
  - source build
  - modules
  - reference
---

# Configure Options

The `./configure` script defines how NGINX is built.

## Files and Permissions

| Option | Description | Default |
|--------|-------------|---------|
| `--prefix=path` | Installation directory | `/usr/local/nginx` |
| `--sbin-path=path` | Executable path | `prefix/sbin/nginx` |
| `--conf-path=path` | Config file path | `prefix/conf/nginx.conf` |
| `--pid-path=path` | PID file path | `prefix/logs/nginx.pid` |
| `--error-log-path=path` | Error log path | `prefix/logs/error.log` |
| `--http-log-path=path` | Access log path | `prefix/logs/access.log` |
| `--user=name` | Worker process user | `nobody` |
| `--group=name` | Worker process group | (same as user) |

## Event Loop

| Option | Description |
|--------|-------------|
| `--with-select_module` | Enable select() method |
| `--without-select_module` | Disable select() method |
| `--with-poll_module` | Enable poll() method |
| `--without-poll_module` | Disable poll() method |

## Optional Modules

| Option | Description |
|--------|-------------|
| `--without-http_gzip_module` | Disable gzip compression |
| `--without-http_rewrite_module` | Disable URL rewriting |
| `--without-http_proxy_module` | Disable HTTP proxying |
| `--with-http_ssl_module` | Enable HTTPS support |
| `--with-pcre=path` | Path to PCRE source |
| `--with-pcre-jit` | Enable PCRE JIT compilation |
| `--with-zlib=path` | Path to zlib source |

## Compilation Controls

| Option | Description |
|--------|-------------|
| `--with-cc-opt=params` | Additional CFLAGS |
| `--with-ld-opt=params` | Additional linker flags |

## Example

```bash
./configure \
    --sbin-path=/usr/local/nginx/nginx \
    --conf-path=/usr/local/nginx/nginx.conf \
    --pid-path=/usr/local/nginx/nginx.pid \
    --with-http_ssl_module \
    --with-pcre=../pcre-8.45 \
    --with-zlib=../zlib-1.2.11
```

## FreeBSD Notes

When using system PCRE on FreeBSD:

```bash
./configure \
    --with-ld-opt="-L /usr/local/lib" \
    --with-cc-opt="-I /usr/local/include"
```

To increase `select()` file descriptor limit:

```bash
--with-cc-opt="-D FD_SETSIZE=2048"
```
