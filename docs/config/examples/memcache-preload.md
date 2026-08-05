---
title: NGINX Memcache Preload with Python FUSE Filesystem
description: Experimental Python FUSE filesystem to preload static content into Memcached for serving via NGINX memcached module.
keywords: nginx memcached, nginx fuse, nginx memcache preload, nginx caching, memcached nginx, nginx python fuse
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - memcached
  - fuse
  - python
  - caching
  - experimental
---

# Memcache Preload with FUSE

!!! warning "Experimental"
    This is a proof of concept.

## Overview

Use a Python FUSE filesystem to preload content into Memcache, then serve via NGINX's memcached module.

## Requirements

- NGINX with memcached module
- Couchbase/Memcached server
- Python with FUSE and memcache libraries

## NGINX Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/;

    location / {
        index index.html;
        default_type text/plain;
        set $memcached_key memfis://hostname$uri;
        memcached_pass 127.0.0.1:11211;
    }
}
```

## Preload Process

```bash
# Mount FUSE filesystem
./memfis.py /mnt/memfis

# Copy content to memcache
cp -a /var/www/* /mnt/memfis

# Unmount
sudo umount /mnt/memfis
```

## MemFiS Filesystem

The `memfis.py` script implements a FUSE filesystem that stores files in Memcache:

- File attributes stored as JSON with `?attr` suffix
- File data stored at the path key
- Directory listings as JSON arrays
- Supports create, read, write, mkdir, symlink operations

The full Python implementation provides additional features for production use.


