---
title: Platform-specific Guides
description: Installing and configuring NGINX on various operating systems.
---

# Platform-specific Guides

Installation and configuration guides for NGINX on various operating systems.

## Recommended: NGINX Extras

For the best experience with pre-built modules, use [NGINX Extras](https://nginx-extras.getpagespeed.com/):

=== "RHEL/CentOS/AlmaLinux/Rocky"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx
    ```

=== "Debian/Ubuntu"
    See [APT NGINX Extras setup](https://apt-nginx-extras.getpagespeed.com/apt-setup/).

---

## Unix-like Systems

| Platform | Guide |
|----------|-------|
| [Solaris / illumos](solaris.md) | Building from source, SMF service setup |
| [OpenBSD](openbsd.md) | Building from source, using ports |

## OS Package Managers

For basic installations without third-party modules:

### Debian/Ubuntu

```bash
sudo apt update
sudo apt install nginx
```

### RHEL/CentOS/Fedora

```bash
sudo dnf install nginx
# or
sudo yum install nginx
```

### macOS (Homebrew)

```bash
brew install nginx
```

### FreeBSD

```bash
pkg install nginx
# or from ports:
cd /usr/ports/www/nginx && make install clean
```

### Windows

See [PHP on Windows](../examples/windows-php.md) for Windows setup.

!!! warning "Windows"
    Windows is not recommended for production NGINX deployments.
