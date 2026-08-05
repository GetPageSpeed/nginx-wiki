---
title: Getting Started with NGINX - Quick Start Installation Guide
description: Get started with NGINX quickly. Install via package managers or source, configure basic settings, and run your first NGINX web server instance.
keywords: NGINX getting started, NGINX quick start, install NGINX, NGINX tutorial, NGINX beginners, first NGINX setup
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - getting started
  - installation
  - quick start
  - tutorial
  - beginners
---

# Getting Started

## Quick Install (Recommended)

The fastest way to install NGINX with modules is using [NGINX Extras](https://nginx-extras.getpagespeed.com/):

=== "RHEL/CentOS/AlmaLinux/Rocky"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx
    sudo systemctl enable --now nginx
    ```

=== "Debian/Ubuntu"
    See [APT NGINX Extras setup](https://apt-nginx-extras.getpagespeed.com/apt-setup/).

---

## Requirements (Source Build)

| Library | Required For |
|---------|--------------|
| zlib | gzip module |
| PCRE/PCRE2 | rewrite module |
| OpenSSL | SSL/TLS support |

Install on your system:

=== "Debian/Ubuntu"
    ```bash
    apt install libpcre3-dev zlib1g-dev libssl-dev
    ```

=== "RHEL/CentOS"
    ```bash
    dnf install pcre-devel zlib-devel openssl-devel
    ```

---

## Installation from Source

Clone from GitHub or download from nginx.org:

```bash
# Extract and configure
tar xzf nginx-*.tar.gz
cd nginx-*
./configure

# Build and install
make
sudo make install
```

By default, NGINX installs to `/usr/local/nginx`. See [installation options](installing.md) for customization.

---

## Running NGINX

### Start

```bash
sudo /usr/local/nginx/sbin/nginx
```

### Reload Configuration

```bash
sudo nginx -s reload
```

Or using signals:

```bash
kill -HUP $(cat /usr/local/nginx/logs/nginx.pid)
```

!!! note "PID File Location"
    The default location is `/usr/local/nginx/logs/nginx.pid`. On Ubuntu, it's `/var/run/nginx.pid`.

---

## Platform-Specific Notes

- **Windows**: [NGINX for Windows (32-bit)](https://kevinworthington.com/nginx-for-windows/)
- **Solaris**: x86/64 builds available
- **macOS**: Install via Homebrew: `brew install nginx`
- **Linux**: Most distributions have packages in their repositories

---

## Next Steps

| Topic | Description |
|-------|-------------|
| [Command-line options](command-line.md) | Process signals and CLI usage |
| [Debugging](debugging.md) | Debug builds and troubleshooting |
| [Optimizations](optimizations.md) | Performance tuning |
| [Pitfalls](pitfalls.md) | Common mistakes to avoid |

