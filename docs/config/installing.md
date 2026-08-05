---
title: Installing and Running NGINX - Complete Installation Guide
description: Install NGINX on Linux, Windows, or from source. Covers package managers, NGINX Extras repository, and building with custom modules.
keywords: NGINX installation, install NGINX, NGINX Linux, NGINX Windows, build NGINX from source, NGINX packages
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - installation
  - setup
  - linux
  - windows
  - source build
  - packages
---

# Installing & running NGINX

For internals work you will often build NGINX from source and run it from a development tree. This page summarises installation options and common development workflows.

## Recommended: NGINX Extras Repository

[NGINX Extras](https://nginx-extras.getpagespeed.com/) provides the latest NGINX with 100+ pre-built modules, making it easy to add functionality without compiling.

### RHEL/CentOS/AlmaLinux/Rocky

=== "RHEL/CentOS 8+, AlmaLinux, Rocky, Amazon Linux 2023"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx
    
    # Optional: Install recommended modules
    sudo dnf -y groupinstall "nginx extras recommended"
    ```

=== "RHEL/CentOS 7, Amazon Linux 2"
    ```bash
    sudo yum -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo yum -y install epel-release
    sudo yum -y install nginx
    ```

### Debian/Ubuntu

See [APT NGINX Extras setup](https://apt-nginx-extras.getpagespeed.com/apt-setup/) for instructions.

### Installing Additional Modules

```bash
# List available modules
sudo dnf list available | grep nginx-module

# Install a module (example: Brotli compression)
sudo dnf -y install nginx-module-brotli
```

---

## Building From Source

For development, testing, or custom builds, compile NGINX from source.

### Quick Start

```bash
# Download latest stable
wget https://nginx.org/download/nginx-1.26.2.tar.gz
tar xzf nginx-1.26.2.tar.gz
cd nginx-1.26.2

# Configure and build
./configure
make
sudo make install
```

By default, NGINX installs to `/usr/local/nginx`.

### Building with Debug Symbols

For internals work and debugging:

```bash
./configure --with-debug
make
sudo make install
```

Or with full debugging symbols and no optimization:

```bash
CFLAGS="-g -O0" ./configure --with-debug
make
sudo make install
```

### Common Configure Options

| Option | Description |
|--------|-------------|
| `--prefix=path` | Set installation prefix (default: `/usr/local/nginx`) |
| `--with-debug` | Enable debug logging |
| `--with-http_ssl_module` | Enable SSL/TLS support |
| `--with-http_v2_module` | Enable HTTP/2 support |
| `--with-http_v3_module` | Enable HTTP/3 (QUIC) support |
| `--with-stream` | Enable TCP/UDP proxy module |
| `--add-module=path` | Add a third-party module |
| `--add-dynamic-module=path` | Add a third-party dynamic module |

See [Compiling NGINX](../modules-dev/compiling.md) for detailed build instructions.

---

## Windows

Download the Windows binary from nginx.org and extract:

```batch
cd c:\
unzip nginx-1.26.2.zip
ren nginx-1.26.2 nginx
cd nginx
start nginx
```

Control:

```batch
nginx -s [ stop | quit | reopen | reload ]
```

For problems look in `c:\nginx\logs\error.log` or EventLog.

!!! warning "Production Use"
    Windows is not recommended for production NGINX deployments. Use Linux for best performance and stability.

---

## After Installing

- See [Examples & recipes](examples/index.md) for configuration examples
- See [Pitfalls and Common Mistakes](pitfalls.md) to avoid common errors
- See [Command-line & process management](command-line.md) to learn how to control NGINX
