---
title: NGINX Systemd Service File Configuration
description: Configure NGINX as a systemd service on Linux with graceful reload, config validation, PID file management, and custom binary paths.
keywords: nginx systemd, nginx service file, nginx linux service, nginx systemctl, nginx daemon, nginx startup
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - systemd
  - linux
  - service management
  - operations
---

# NGINX Systemd Service File

Works on Fedora, OpenSUSE, Arch Linux, Ubuntu, and most modern Linux distributions.

!!! note "Paths"
    The `PIDFile` and NGINX binary locations may differ depending on how NGINX was compiled.

---

## Service File

Save as `/lib/systemd/system/nginx.service`:

```ini
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=syslog.target network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/usr/sbin/nginx -s reload
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

---

## Key Directives

| Directive | Purpose |
|-----------|---------|
| `Type=forking` | NGINX forks to background after starting |
| `ExecStartPre` | Validate config before starting |
| `ExecReload` | Graceful reload with `-s reload` |
| `ExecStop` | Graceful shutdown with `QUIT` signal |
| `PrivateTmp` | Security: isolate /tmp from other processes |

---

## Usage

```bash
# Enable service at boot
sudo systemctl enable nginx

# Start service
sudo systemctl start nginx

# Reload configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx

# Stop service
sudo systemctl stop nginx
```

---

## Custom Binary Path

If NGINX is installed in a non-standard location, adjust the paths:

```ini
[Service]
ExecStartPre=/opt/nginx/sbin/nginx -t -c /opt/nginx/conf/nginx.conf
ExecStart=/opt/nginx/sbin/nginx -c /opt/nginx/conf/nginx.conf
ExecReload=/opt/nginx/sbin/nginx -s reload -c /opt/nginx/conf/nginx.conf
PIDFile=/opt/nginx/logs/nginx.pid
```


