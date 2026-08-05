---
title: NGINX macOS Launchd Daemon Configuration
description: Configure NGINX as a launchd daemon on macOS with automatic startup, plist configuration, and launchctl service management.
keywords: nginx macos, nginx launchd, nginx plist, nginx mac daemon, nginx osx, launchctl nginx
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - macos
  - launchd
  - daemon
  - plist
---

# macOS Launchd

## Plist Configuration

Save as `/Library/LaunchDaemons/nginx.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
                        "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>nginx</string>
    <key>Program</key>
    <string>/usr/local/sbin/nginx</string>
    <key>KeepAlive</key>
    <true/>
    <key>NetworkState</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/var/log/system.log</string>
    <key>LaunchOnlyOnce</key>
    <true/>
  </dict>
</plist>
```

## Load the Service

```bash
sudo launchctl load -F /Library/LaunchDaemons/nginx.plist
```

## Unload the Service

```bash
sudo launchctl unload /Library/LaunchDaemons/nginx.plist
```

!!! note
    This launches NGINX automatically on boot. Errors are logged to syslog; NGINX typically logs to `/usr/local/var/log/nginx/error.log`.


