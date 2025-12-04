---
title: Log Rotation
description: How to rotate NGINX logs using the USR1 signal.
---

# Log Rotation

NGINX re-opens its logs in response to the `USR1` signal.

## Basic Rotation Script

```bash
mv access.log access.log.0
kill -USR1 `cat /var/run/nginx.pid`
sleep 1
gzip access.log.0  # or any other processing
```

!!! note "Why `sleep 1`?"
    After sending `USR1`, NGINX needs a moment to finish writing to the old file descriptor before you can safely compress/process the old log.

---

## Logrotate Configuration

For systems using logrotate, create `/etc/logrotate.d/nginx`:

```
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

| Directive | Purpose |
|-----------|---------|
| `daily` | Rotate logs daily |
| `rotate 14` | Keep 14 days of logs |
| `compress` | Compress rotated logs with gzip |
| `delaycompress` | Delay compression by one rotation |
| `sharedscripts` | Run postrotate only once for all logs |
| `postrotate` | Send USR1 signal after rotation |

---

## How It Works

1. The log file is moved/renamed
2. NGINX continues writing to the old file descriptor
3. `USR1` signal tells NGINX to re-open log files
4. NGINX opens new log files with the original names
5. Old log files can now be safely processed

!!! tip "Access vs Error Logs"
    Both `access_log` and `error_log` are reopened on `USR1`.


