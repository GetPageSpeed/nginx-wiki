---
title: Installing and Compiling NGINX - Build From Source Guide
description: Complete guide to installing NGINX from packages and compiling from source. Learn build options, module compilation, and debug builds.
keywords: NGINX compile, build NGINX from source, NGINX installation, NGINX modules, configure NGINX, make NGINX
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - compilation
  - installation
  - build-from-source
  - modules
  - configure
  - make
---

# Installing & Compiling NGINX

This guide covers installing NGINX from packages (recommended) and building from source when needed.

---

## Installing from Packages (Recommended)

For most users, installing pre-built packages is faster and easier to maintain.

### Using NGINX Extras Repository

[NGINX Extras](https://nginx-extras.getpagespeed.com/) provides NGINX with 100+ pre-built modules.

=== "RHEL/CentOS 8+, AlmaLinux, Rocky, Amazon Linux 2023"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx
    
    # Install with recommended modules (PageSpeed, Brotli, ModSecurity)
    sudo dnf -y groupinstall "nginx extras recommended"
    ```

=== "RHEL/CentOS 7, Amazon Linux 2"
    ```bash
    sudo yum -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo yum -y install epel-release
    sudo yum -y install nginx
    ```

=== "Debian/Ubuntu"
    See [APT NGINX Extras setup](https://apt-nginx-extras.getpagespeed.com/apt-setup/) for instructions.

### Installing Modules

```bash
# List available modules
sudo dnf list available | grep nginx-module

# Install a specific module
sudo dnf -y install nginx-module-brotli

# Enable in nginx.conf
load_module modules/ngx_http_brotli_filter_module.so;
load_module modules/ngx_http_brotli_static_module.so;
```

### Upgrading

```bash
# Update packages
sudo dnf upgrade nginx nginx-module-*

# Apply without downtime
sudo service nginx upgrade
```

---

## Building from Source

Compile NGINX when you need custom patches or modules not available as packages.

### Prerequisites

#### Build Tools

=== "Debian/Ubuntu"
    ```bash
    apt update
    apt install build-essential git
    ```

=== "RHEL/CentOS"
    ```bash
    yum groupinstall "Development Tools"
    yum install git
    ```

=== "macOS"
    ```bash
    xcode-select --install
    brew install git
    ```

#### Dependencies

=== "Debian/Ubuntu"
    ```bash
    apt install libpcre3-dev zlib1g-dev libssl-dev \
                libgeoip-dev libxslt1-dev libgd-dev
    ```

=== "RHEL/CentOS"
    ```bash
    yum install pcre-devel zlib-devel openssl-devel \
                geoip-devel libxslt-devel gd-devel
    ```

=== "macOS"
    ```bash
    brew install pcre zlib openssl libgeoip libxslt gd
    ```

---

## Download NGINX Source

```bash
# Download latest stable
wget https://nginx.org/download/nginx-1.24.0.tar.gz
tar -xzf nginx-1.24.0.tar.gz
cd nginx-1.24.0

# Or clone from repository
git clone https://github.com/nginx/nginx.git
cd nginx
```

---

## Basic Build

### Minimal Build

```bash
./configure
make
sudo make install
```

Default install location: `/usr/local/nginx`

### Production Build

```bash
./configure \
    --prefix=/etc/nginx \
    --sbin-path=/usr/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --pid-path=/var/run/nginx.pid \
    --lock-path=/var/run/nginx.lock \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_gzip_static_module \
    --with-http_stub_status_module \
    --with-threads \
    --with-file-aio

make -j$(nproc)
sudo make install
```

---

## Adding Modules

### Static Modules (Compiled In)

```bash
./configure --add-module=/path/to/my_module

# Multiple modules
./configure \
    --add-module=/path/to/module1 \
    --add-module=/path/to/module2
```

### Dynamic Modules (Loadable)

```bash
./configure --add-dynamic-module=/path/to/my_module

make modules
```

Output: `objs/ngx_http_mymodule_module.so`

Load in nginx.conf:

```nginx
load_module modules/ngx_http_mymodule_module.so;
```

---

## Module File Structure

### Minimal Structure

```
my_module/
├── config              # Build configuration
└── ngx_http_mymodule.c # Source code
```

### config File (Legacy)

```bash
# config
ngx_addon_name=ngx_http_mymodule_module

# For HTTP modules
HTTP_MODULES="$HTTP_MODULES ngx_http_mymodule_module"
NGX_ADDON_SRCS="$NGX_ADDON_SRCS $ngx_addon_dir/ngx_http_mymodule.c"

# For Stream modules
# STREAM_MODULES="$STREAM_MODULES ngx_stream_mymodule_module"

# Additional dependencies
NGX_ADDON_DEPS="$NGX_ADDON_DEPS $ngx_addon_dir/ngx_http_mymodule.h"

# Libraries
CORE_LIBS="$CORE_LIBS -lmylib"
```

### config File (Modern - NGINX 1.9.11+)

```bash
# config
ngx_addon_name=ngx_http_mymodule_module
ngx_module_type=HTTP
ngx_module_name=ngx_http_mymodule_module
ngx_module_srcs="$ngx_addon_dir/ngx_http_mymodule.c"

# Optional
ngx_module_deps="$ngx_addon_dir/ngx_http_mymodule.h"
ngx_module_libs="-lmylib"
ngx_module_order="ngx_http_mymodule_module \
                  ngx_http_copy_filter_module"

. auto/module
```

---

## Debug Build

### Enable Debug Symbols

```bash
./configure \
    --with-debug \
    --with-cc-opt="-O0 -g -DNGX_DEBUG_MALLOC"

make
```

### Debug Logging

```nginx
error_log /var/log/nginx/debug.log debug;

events {
    debug_connection 127.0.0.1;
}
```

### Core Dumps

```bash
# Set core dump size
ulimit -c unlimited

# Configure core dump location (Linux)
echo "/tmp/nginx-core.%p" > /proc/sys/kernel/core_pattern
```

```nginx
# Enable in NGINX
working_directory /tmp;
worker_rlimit_core 500M;
```

---

## Build Options Reference

### Path Options

| Option | Description |
|--------|-------------|
| `--prefix=PATH` | Installation prefix |
| `--sbin-path=PATH` | nginx binary path |
| `--conf-path=PATH` | Config file path |
| `--error-log-path=PATH` | Error log path |
| `--pid-path=PATH` | PID file path |
| `--lock-path=PATH` | Lock file path |
| `--modules-path=PATH` | Dynamic modules path |

### HTTP Modules

| Option | Description |
|--------|-------------|
| `--with-http_ssl_module` | HTTPS support |
| `--with-http_v2_module` | HTTP/2 support |
| `--with-http_realip_module` | Real IP from proxy headers |
| `--with-http_gzip_static_module` | Pre-compressed files |
| `--with-http_auth_request_module` | Auth subrequests |
| `--with-http_stub_status_module` | Status page |
| `--with-http_sub_module` | Response substitution |

### Performance Options

| Option | Description |
|--------|-------------|
| `--with-threads` | Thread pool support |
| `--with-file-aio` | Async file I/O (Linux) |
| `--with-http_slice_module` | Range request caching |

### Compiler Options

| Option | Description |
|--------|-------------|
| `--with-cc=PATH` | C compiler path |
| `--with-cc-opt=OPTIONS` | Additional compiler flags |
| `--with-ld-opt=OPTIONS` | Additional linker flags |
| `--with-cpu-opt=CPU` | CPU optimization |

---

## Building Third-Party Modules

!!! tip "Use Pre-Built Modules"
    Most popular modules are available as packages from [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/). This saves compilation time and ensures compatibility.
    
    ```bash
    # Instead of compiling headers-more:
    sudo dnf -y install nginx-module-headers-more
    ```

### Example: Headers More Module (Manual Build)

```bash
# Download module
git clone https://github.com/openresty/headers-more-nginx-module.git

# Build with NGINX
cd nginx-1.24.0
./configure --add-module=../headers-more-nginx-module
make
sudo make install
```

### Example: Dynamic Module

```bash
./configure \
    --add-dynamic-module=../headers-more-nginx-module \
    --with-compat

make modules

sudo cp objs/ngx_http_headers_more_filter_module.so /etc/nginx/modules/
```

---

## Cross-Compilation

For embedded systems or different architectures:

```bash
./configure \
    --crossbuild=Linux:arm \
    --with-cc=arm-linux-gnueabihf-gcc \
    --with-cpp=arm-linux-gnueabihf-cpp \
    --with-cc-opt="-march=armv7-a" \
    --without-http_rewrite_module \
    --without-http_gzip_module
```

---

## Troubleshooting

### Common Errors

**PCRE library not found:**
```bash
apt install libpcre3-dev  # Debian/Ubuntu
yum install pcre-devel    # RHEL/CentOS
```

**OpenSSL not found:**
```bash
./configure --with-openssl=/path/to/openssl
# Or install system package
apt install libssl-dev
```

**Module compatibility:**
```bash
# Check NGINX version in module
nginx -V 2>&1 | grep "nginx version"

# Rebuild module for current NGINX
./configure --add-dynamic-module=/path/to/module --with-compat
```

### Checking Build Configuration

```bash
# Show compile options of installed NGINX
nginx -V

# Sample output:
# nginx version: nginx/1.24.0
# built with OpenSSL 1.1.1
# configure arguments: --with-http_ssl_module --with-http_v2_module ...
```

---

## Makefile Targets

```bash
make                # Build nginx binary
make modules        # Build dynamic modules only
make install        # Install to prefix
make upgrade        # Hot upgrade binary

# Clean build
make clean
```

---

## Development Workflow

### Incremental Build

```bash
# Initial build
./configure --add-module=/path/to/mymodule --with-debug
make

# After source changes
make

# Test
objs/nginx -t -c /path/to/test.conf
```

### Quick Test Setup

```bash
# Create minimal test config
cat > /tmp/nginx.conf << 'EOF'
daemon off;
master_process off;
error_log stderr debug;
events { }
http {
    server {
        listen 8080;
        location /test {
            my_directive;
        }
    }
}
EOF

# Run
objs/nginx -c /tmp/nginx.conf
```

---

## Next Steps

- [Configuration Directives](configuration.md) - Define module directives
- [Module API](../core-apis/module-api.md) - Full API reference
- [Working Examples](examples/index.md) - Complete module examples
