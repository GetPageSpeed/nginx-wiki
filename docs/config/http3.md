---
title: HTTP/3 (QUIC)
description: Configure NGINX with HTTP/3 and QUIC protocol support.
---

# HTTP/3 (QUIC)

HTTP/3 uses QUIC as its transport protocol, providing faster connections and improved performance, especially on unreliable networks.

---

## Requirements

- NGINX 1.25.0+ (mainline) with QUIC support
- OpenSSL 3.0+ or BoringSSL/quictls
- UDP port 443 open in firewall

### Check NGINX Support

```bash
nginx -V 2>&1 | grep -o 'http_v3_module'
```

---

## Basic HTTP/3 Configuration

```nginx
server {
    # HTTP/3 (QUIC) - UDP
    listen 443 quic reuseport;
    listen [::]:443 quic reuseport;

    # HTTP/2 and HTTP/1.1 - TCP (fallback)
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;

    server_name example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS 1.3 required for HTTP/3
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Advertise HTTP/3 support to clients
    add_header Alt-Svc 'h3=":443"; ma=86400' always;

    # HTTP/3 is enabled by default (http3 on;)
    # Optional: Enable address validation
    quic_retry on;

    root /var/www/html;
    index index.html;
}
```

!!! note "Defaults (NGINX 1.25+)"
    - `http3` defaults to `on` - no need to specify
    - `quic_retry` defaults to `off` - enable for DDoS protection
    - `quic_gso` defaults to `off` - enable for performance on supported systems

---

## Full Production Configuration

```nginx
server {
    # HTTP redirect
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    # QUIC and HTTP/3 (UDP)
    listen 443 quic reuseport;
    listen [::]:443 quic reuseport;

    # HTTP/1.1 and HTTP/2 fallback (TCP)
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;

    server_name example.com www.example.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS settings (TLS 1.3 required for HTTP/3)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    # QUIC settings (http3 is on by default)
    quic_retry on;      # Address validation (DDoS protection)
    quic_gso on;        # Generic Segmentation Offload (performance)

    # Advertise HTTP/3 availability to clients
    add_header Alt-Svc 'h3=":443"; ma=86400' always;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Root and index
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## QUIC-Specific Directives

| Directive | Description | Default |
|-----------|-------------|---------|
| `http3` | Enable HTTP/3 | `on` |
| `http3_hq` | Enable HQ (HTTP/0.9 over QUIC) | `off` |
| `http3_max_concurrent_streams` | Max streams per connection | `128` |
| `http3_stream_buffer_size` | Buffer size per stream | `64k` |
| `quic_retry` | Enable address validation (recommended) | `off` |
| `quic_gso` | Enable Generic Segmentation Offload | `off` |
| `quic_active_connection_id_limit` | Max connection IDs | `2` |
| `quic_host_key` | Host key file for QUIC | (auto-generated) |

!!! info "http3 vs listen quic"
    The `listen 443 quic` directive enables the QUIC listener. The `http3` directive (default `on`) enables HTTP/3 protocol negotiation on QUIC connections. Both are needed for HTTP/3 to work.

---

## Firewall Configuration

Open UDP port 443:

=== "iptables"
    ```bash
    iptables -A INPUT -p udp --dport 443 -j ACCEPT
    ip6tables -A INPUT -p udp --dport 443 -j ACCEPT
    ```

=== "firewalld"
    ```bash
    firewall-cmd --permanent --add-port=443/udp
    firewall-cmd --reload
    ```

=== "ufw"
    ```bash
    ufw allow 443/udp
    ```

---

## Installing NGINX with HTTP/3

### Pre-Built Packages (Recommended)

The easiest way to get HTTP/3 support:

=== "RHEL/CentOS/AlmaLinux"
    ```bash
    sudo dnf install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf install nginx-quic
    ```
    
    See [NGINX Extras HTTP/3 packages](https://nginx-extras.getpagespeed.com/distributions/http3/) for details.

=== "Debian/Ubuntu"
    See [APT NGINX Extras](https://apt-nginx-extras.getpagespeed.com/apt-setup/) for packages with QUIC support.

### Building from Source

If you need to build from source with HTTP/3 support:

```bash
# Clone quictls (OpenSSL fork with QUIC support)
git clone --depth 1 -b openssl-3.1.4+quic https://github.com/quictls/openssl

# Download NGINX
wget https://nginx.org/download/nginx-1.25.3.tar.gz
tar xzf nginx-1.25.3.tar.gz
cd nginx-1.25.3

# Build NGINX with HTTP/3
./configure \
    --with-http_v3_module \
    --with-http_ssl_module \
    --with-openssl=../openssl \
    --with-openssl-opt=enable-ktls

make
sudo make install
```

---

## Proxy with HTTP/3

### HTTP/3 to Backend (HTTP/1.1)

```nginx
upstream backend {
    server 127.0.0.1:8080;
    keepalive 32;
}

server {
    listen 443 quic reuseport;
    listen 443 ssl;
    http2 on;

    # ... SSL config ...

    # http3 is on by default
    add_header Alt-Svc 'h3=":443"; ma=86400' always;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
}
```

---

## 0-RTT (Early Data)

Enable 0-RTT for faster connections (with caution):

```nginx
ssl_early_data on;

location / {
    # Protect against replay attacks
    proxy_set_header Early-Data $ssl_early_data;
}
```

!!! warning "Security Note"
    0-RTT data is vulnerable to replay attacks. Only enable for idempotent requests (GET, HEAD) and ensure backend handles the `Early-Data` header.

---

## Testing HTTP/3

### Using curl

```bash
# curl 7.66+ with HTTP/3 support
curl --http3 https://example.com

# Check which protocol was used
curl -sI --http3 https://example.com | grep -i alt-svc
```

### Using Chrome DevTools

1. Open DevTools (F12)
2. Go to Network tab
3. Right-click column headers → Enable "Protocol"
4. Look for "h3" protocol

### Using Online Tools

- HTTP/3 Check: Test your site's HTTP/3 support
- Qualys SSL Labs: Shows HTTP/3 in protocol support

---

## Performance Tuning

### Kernel Settings

```bash
# /etc/sysctl.conf
net.core.rmem_max = 2500000
net.core.wmem_max = 2500000

# Apply
sysctl -p
```

### NGINX Worker Settings

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}
```

---

## Logging HTTP/3

```nginx
log_format quic '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent" '
                '$http3 $ssl_protocol';

access_log /var/log/nginx/access.log quic;
```

Variable `$http3` returns "h3" for HTTP/3 connections.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure UDP port 443 is open |
| Falls back to HTTP/2 | Check TLS 1.3 is enabled |
| No Alt-Svc header | Add `add_header Alt-Svc` directive |
| Performance worse than HTTP/2 | Tune kernel buffers, check network |

---

## See Also

- [SSL/TLS Configuration](ssl.md)
- [Load Balancing](load-balancing.md)
- [Performance Tuning](../architecture/event-loop.md)

