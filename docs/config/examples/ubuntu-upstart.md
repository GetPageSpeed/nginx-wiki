---
title: NGINX Ubuntu Upstart Init Configuration (Legacy)
description: Configure NGINX with Ubuntu Upstart init system for automatic startup, respawning, and graceful configuration testing on older systems.
keywords: nginx upstart, nginx ubuntu, nginx init, nginx respawn, upstart configuration, nginx legacy
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - ubuntu
  - upstart
  - init
  - legacy
---

# Ubuntu Upstart

!!! note "Legacy"
    Upstart is legacy. Modern Ubuntu uses systemd. See [Systemd](systemd.md).

## Upstart Configuration

Save as `/etc/init/nginx.conf`:

```bash
# nginx

description "nginx http daemon"
author "George Shammas <georgyo@gmail.com>"

start on (filesystem and net-device-up IFACE!=lo)
stop on runlevel [!2345]

env DAEMON=/usr/sbin/nginx
env PID=/var/run/nginx.pid

expect fork
respawn
respawn limit 10 5

pre-start script
    $DAEMON -t
    if [ $? -ne 0 ]
        then exit $?
    fi
end script

exec $DAEMON
```

## Commands

Reload configuration:

```bash
initctl reload-configuration
```

Check status:

```bash
initctl list | grep nginx
```

Start NGINX:

```bash
initctl start nginx
```

## Configuration Notes

- `respawn` - Keeps NGINX master process alive
- `expect fork` - Tracks NGINX after forking
- `respawn limit 10 5` - Stop if respawned >10 times in 5 seconds
- `pre-start script` - Tests config before starting


