---
title: Nchan
description: Scalable pub/sub server for WebSockets, EventSource, and Long-Poll.
---

# Nchan

**Nchan** is a scalable, flexible pub/sub server for the modern web, built as an NGINX module.

:octicons-repo-16: **Repository**: [slact/nchan](https://github.com/slact/nchan)  
:octicons-package-16: **NGINX Extras**: [nginx-module-nchan](https://nginx-extras.getpagespeed.com/modules/nchan/)

---

## Installation

=== "RHEL/CentOS/AlmaLinux/Rocky (Recommended)"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx-module-nchan
    ```
    
    Enable in `/etc/nginx/nginx.conf`:
    ```nginx
    load_module modules/ngx_nchan_module.so;
    ```

=== "From Source"
    ```bash
    git clone https://github.com/slact/nchan.git
    cd nginx-1.x.x
    ./configure --add-module=../nchan
    make && sudo make install
    ```

---

## Features

- **Standalone or shim** — Run as a dedicated server or between your app and subscribers
- **Multiple protocols** — WebSockets, EventSource (SSE), Long-Polling, HTTP Streaming
- **Scalable** — Handles thousands to millions of concurrent connections
- **Flexible storage** — Memory, on-disk, or Redis for message buffering
- **Horizontal scaling** — Multiple NGINX instances with Redis backend
- **Channel multiplexing** — Each subscriber can listen to up to 4 channels
- **Authentication** — Custom application URL for subscriber verification
- **Debug channel** — Events meta channel for debugging

## Publishing & Subscribing

- **Publish**: HTTP POST or WebSocket
- **Subscribe**: WebSocket, Long-Polling, EventSource, Interval Polling

## History

Nchan was originally the **Nginx HTTP Push Module**. It was renamed after a complete refactoring and overhaul.

## Quick Example

```nginx
# Publisher endpoint
location /pub {
    nchan_publisher;
    nchan_channel_id $arg_id;
}

# Subscriber endpoint (WebSocket, EventSource, Long-Poll)
location /sub {
    nchan_subscriber;
    nchan_channel_id $arg_id;
}
```

See the [NGINX Extras documentation](https://nginx-extras.getpagespeed.com/modules/nchan/) for configuration details.


