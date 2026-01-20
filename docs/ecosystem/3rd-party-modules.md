---
title: NGINX 3rd-Party Modules Catalog - Community Extensions
description: Complete catalog of community-maintained NGINX modules for caching, security, Lua scripting, load balancing, and more.
keywords: nginx modules, nginx extensions, nginx lua, nginx security, nginx caching, nginx load balancing, third party modules
author: NGINX Community
date: 2024-01-01
updated: 2025-01-21
schema_type: TechArticle
tags:
  - modules
  - extensions
  - third-party
  - caching
  - security
  - lua
  - load-balancing
---

# 3rd-Party Modules Catalog

Community-maintained modules that extend NGINX functionality.

!!! tip "Easy Installation with NGINX Extras"
    For RHEL/CentOS/AlmaLinux/Rocky Linux users, [NGINX Extras](https://nginx-extras.getpagespeed.com/) provides pre-built module packages. No compiling needed!
    
    For Debian/Ubuntu users, see [APT NGINX Extras](https://apt-nginx-extras.getpagespeed.com/apt-setup/).

---

## Installing Pre-Built Modules

=== "RHEL/CentOS 8+, AlmaLinux, Rocky"
    ```bash
    dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    dnf -y install nginx-module-<name>
    ```

=== "RHEL/CentOS 7, Amazon Linux 2"
    ```bash
    yum -y install https://extras.getpagespeed.com/release-latest.rpm
    yum -y install epel-release
    yum -y install nginx-module-<name>
    ```

=== "Debian/Ubuntu"
    See [APT setup instructions](https://apt-nginx-extras.getpagespeed.com/apt-setup/).
    
    !!! tip "Auto-enabled"
        Debian/Ubuntu packages automatically enable modules — no `load_module` needed!

**RHEL-based systems only:** After installing, enable the module in `/etc/nginx/nginx.conf`:

```nginx
load_module modules/ngx_http_<name>_module.so;
```

---

## Detailed Documentation

These modules have in-depth documentation in this wiki:

| Module | Description |
|--------|-------------|
| [Upload](modules/upload.md) | File upload handling with multipart/form-data |
| [Nchan](modules/nchan.md) | Pub/sub for WebSockets, EventSource, Long-Poll |

---

## Popular Modules

### Content & Templating

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Echo** | Shell-style commands (echo, sleep, exec) | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/echo/) |
| **Lua** | Embed Lua scripts in NGINX | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/lua/) |
| **Perl** | Embed Perl (built-in, `--with-http_perl_module`) | Built-in |
| **Substitutions** | Regex-based response body substitution | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/substitutions/) |
| **Headers More** | Set/clear input/output headers | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/headers-more/) |
| **Fancy Index** | Customizable directory listings | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/fancyindex/) |

### Caching & Performance

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Brotli** | Brotli compression | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/brotli/) |
| **Redis2** | Full Redis 2.0 protocol support | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/redis2/) |
| **Memc** | Memcached protocol with full support | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/memc/) |
| **SRCache** | Transparent subrequest caching | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/srcache/) |
| **PageSpeed** | Google PageSpeed optimization | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/pagespeed/) |

### Load Balancing

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Upstream Fair** | Fair load balancing algorithm | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/upstream-fair/) |
| **Upstream JDomain** | Dynamic DNS resolution for upstreams | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/upstream-jdomain/) |
| **Upsync** | Dynamic upstream configuration | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/upsync/) |

### Security & Access Control

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Auth Digest** | RFC 2617 Digest Authentication | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/auth-digest/) |
| **Auth PAM** | PAM authentication | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/auth-pam/) |
| **Auth LDAP** | LDAP authentication | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/auth-ldap/) |
| **Auth TOTP** | Time-based One-Time Password | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/auth-totp/) |
| **NAXSI** | Web Application Firewall | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/naxsi/) |
| **ModSecurity** | WAF with OWASP Core Rule Set | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/security/) |
| **Security Headers** | Add security headers automatically | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/security-headers/) |

### Real-time & Push

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Nchan** | Pub/sub (WebSocket, SSE, Long-Poll) | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/nchan/) |
| **Push Stream** | Push/streaming capabilities | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/push-stream/) |

### File Handling

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Upload** | Multipart file upload handling | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/upload/) |
| **ZIP** | Create ZIP archives on-the-fly | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/zip/) |
| **Untar** | Serve files from tar archives | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/untar/) |

### Media & Streaming

| Module | Description | Documentation |
|--------|-------------|---------------|
| **RTMP** | RTMP/HLS/DASH streaming | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/rtmp/) |
| **VOD** | On-the-fly HLS/DASH from MP4 | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/vod/) |
| **Image Filter** | On-the-fly image transformation | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/image-filter/) |
| **Small Light** | Advanced image transformation | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/small-light/) |

### Utilities

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Set Misc** | Additional set directives | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/set-misc/) |
| **Form Input** | Parse POST form data | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/form-input/) |
| **Array Var** | Array variables | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/array-var/) |
| **Iconv** | Character encoding conversion | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/iconv/) |
| **GeoIP2** | MaxMind GeoIP2 database support | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/geoip2/) |
| **NJS** | JavaScript scripting | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/njs/) |

### Logging & Monitoring

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Log ZMQ** | ZeroMQ log publishing | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/log-zmq/) |
| **VTS** | Virtual host traffic status | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/vts/) |
| **STS** | Stream traffic status | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/sts/) |
| **Graphite** | Send metrics to Graphite | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/graphite/) |

### Development & Helper

| Module | Description | Documentation |
|--------|-------------|---------------|
| **NDK** | Nginx Development Kit (required by many modules) | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/ndk/) |
| **Cache Purge** | Purge content from cache | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/cache-purge/) |
| **DAV Ext** | Extended WebDAV support | [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/dav-ext/) |

---

## Complete Module List

For a complete list of available modules with documentation:

- **RPM-based distros**: [NGINX Extras Modules](https://nginx-extras.getpagespeed.com/modules/)
- **Lua libraries**: [NGINX Extras Lua Scripting](https://nginx-extras.getpagespeed.com/lua-scripting/)

---

## Lua Scripting

For Lua scripting in NGINX, you have several options:

- **NGINX Extras**: Install `nginx-module-lua` from [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/lua/) for RPM-based systems
- **Lua Libraries**: Browse [available Lua libraries](https://nginx-extras.getpagespeed.com/lua-scripting/) for common tasks
- **OpenResty**: A full distribution bundling NGINX with LuaJIT (useful if you need many Lua modules)

---

## Recommended Module Groups

For quick setup, NGINX Extras provides module groups:

```bash
# Performance and security essentials
sudo dnf -y groupinstall "nginx extras recommended"
```

This installs: PageSpeed, Brotli, Dynamic ETag, Immutable (performance) and ModSecurity, Security Headers (security).

---

## Upgrading Modules

After updating module packages:

```bash
# Apply updates at runtime
sudo service nginx upgrade
```

This performs a binary upgrade without dropping connections.

---

## Configuration Tools

These standalone tools help you analyze and validate NGINX configurations:

| Tool | Description | Link |
|------|-------------|------|
| **Gixy** | Static analyzer for NGINX configs, detects security misconfigurations | [gixy.org](https://gixy.org/) |
| **nginx-config-formatter** | Formats and beautifies nginx configs | [GitHub](https://github.com/1connect/nginx-config-formatter) |
| **crossplane** | Parse and analyze NGINX configs programmatically | [GitHub](https://github.com/nginxinc/crossplane) |

```bash
# Install Gixy
pip install gixy

# Analyze your configuration
gixy /etc/nginx/nginx.conf
```

---

## Contributing

To suggest additions or corrections to this catalog, please contact the maintainers.
