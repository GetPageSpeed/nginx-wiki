---
title: Security Hardening
description: Comprehensive security hardening guide for NGINX.
---

# Security Hardening

Comprehensive guide to securing your NGINX installation and protecting web applications.

---

## Security Headers

### Essential Headers

```nginx
# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# XSS protection (legacy browsers)
add_header X-XSS-Protection "1; mode=block" always;

# Control referrer information
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Force HTTPS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; frame-ancestors 'self';" always;

# Permissions Policy
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Reusable Snippet

Create `/etc/nginx/snippets/security-headers.conf`:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

Include in server blocks:

```nginx
server {
    include snippets/security-headers.conf;
    # ...
}
```

---

## Rate Limiting

### Basic Rate Limiting

```nginx
# Define zones (http block)
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    # General rate limit
    limit_req zone=general burst=20 nodelay;
    limit_conn addr 10;

    # Strict limit on login
    location /login {
        limit_req zone=login burst=5 nodelay;
        # ...
    }

    # API rate limit
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        # ...
    }
}
```

### Rate Limit by API Key

```nginx
map $http_x_api_key $api_client {
    default         "anonymous";
    "key123abc"     "client_a";
    "key456def"     "client_b";
}

limit_req_zone $api_client zone=api_by_key:10m rate=100r/s;

location /api/ {
    limit_req zone=api_by_key burst=200 nodelay;
}
```

---

## Block Malicious Requests

### Block User Agents

```nginx
# Block bad bots and scanners
if ($http_user_agent ~* (nikto|sqlmap|netsparker|acunetix|nessus|openvas|w3af|burpsuite|havij|appscan)) {
    return 403;
}

# Block empty user agents
if ($http_user_agent = "") {
    return 403;
}
```

### Block Suspicious Patterns

```nginx
# Block SQL injection attempts
location / {
    if ($query_string ~* "(union|select|insert|update|delete|drop|truncate|alter|exec|execute).*(\(|%28)") {
        return 403;
    }

    # Block path traversal
    if ($request_uri ~* "\.\.") {
        return 403;
    }

    # Block script injections
    if ($query_string ~* "<script|javascript:|vbscript:|onclick|onerror") {
        return 403;
    }
}
```

### Block by Country (GeoIP2)

```nginx
# Requires ngx_http_geoip2_module
geoip2 /usr/share/GeoIP/GeoLite2-Country.mmdb {
    $geoip2_country_code country iso_code;
}

map $geoip2_country_code $blocked_country {
    default 0;
    XX      1;  # Block country XX
    YY      1;  # Block country YY
}

server {
    if ($blocked_country) {
        return 403;
    }
}
```

---

## File Access Protection

### Block Hidden Files

```nginx
# Block all dotfiles except .well-known
location ~ /\.(?!well-known) {
    deny all;
}
```

### Block Sensitive Files

```nginx
# Block common sensitive files
location ~* (?:\.(?:bak|conf|dist|fla|in[ci]|log|orig|psd|sh|sql|sw[op])|~)$ {
    deny all;
}

# Block version control
location ~ /\.(?:git|svn|hg)/ {
    deny all;
}

# Block composer/npm files
location ~* (?:composer\.json|composer\.lock|package\.json|package-lock\.json)$ {
    deny all;
}
```

### Block PHP in Upload Directories

```nginx
location ~* /(?:uploads|files|media|images)/.*\.php$ {
    deny all;
}
```

---

## Request Filtering

### Limit Request Size

```nginx
# Limit body size
client_max_body_size 10m;

# Limit header size
client_header_buffer_size 1k;
large_client_header_buffers 4 8k;

# Limit URI length
# Note: This requires recompiling NGINX with custom settings
```

### Limit Request Methods

```nginx
# Allow only specific methods
if ($request_method !~ ^(GET|HEAD|POST|PUT|DELETE|OPTIONS)$) {
    return 405;
}

# For static files, allow only GET/HEAD
location ~* \.(js|css|png|jpg|gif|ico|svg|woff|woff2)$ {
    limit_except GET HEAD {
        deny all;
    }
    expires 1y;
}
```

### Block Specific URIs

```nginx
# Block common attack paths
location ~* (?:wp-config\.php|xmlrpc\.php|\.env|\.git|\.htaccess) {
    deny all;
}

# Block PHP info
location ~* /(?:phpinfo|info)\.php$ {
    deny all;
}
```

---

## SSL/TLS Security

### Secure SSL Configuration

```nginx
# Modern protocols only
ssl_protocols TLSv1.2 TLSv1.3;

# Secure ciphers
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

# Session settings
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

See [SSL/TLS Configuration](ssl.md) for complete guide.

---

## IP Allowlisting

### Admin Area Protection

```nginx
location /admin {
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    allow 172.16.0.0/12;
    deny all;

    # Still require authentication
    auth_basic "Admin Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### Maintenance Mode with Bypass

```nginx
geo $maintenance {
    default         1;
    10.0.0.0/8      0;  # Allow internal IPs
    203.0.113.50    0;  # Allow specific IP
}

server {
    if ($maintenance) {
        return 503;
    }

    error_page 503 @maintenance;
    location @maintenance {
        root /var/www/maintenance;
        rewrite ^(.*)$ /maintenance.html break;
    }
}
```

---

## Authentication

### Basic Authentication

```bash
# Create password file
htpasswd -c /etc/nginx/.htpasswd admin
```

```nginx
location /secure {
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### Auth Request (Subrequest)

```nginx
location /api {
    auth_request /auth;
    auth_request_set $user $upstream_http_x_user;
    proxy_set_header X-User $user;
    proxy_pass http://backend;
}

location = /auth {
    internal;
    proxy_pass http://auth-service/validate;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header X-Original-URI $request_uri;
}
```

---

## Logging for Security

### Enhanced Access Log

```nginx
log_format security '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time $upstream_response_time '
                    '"$http_x_forwarded_for" "$ssl_protocol" "$ssl_cipher"';

access_log /var/log/nginx/security.log security;
```

### Log Suspicious Requests

```nginx
map $status $loggable {
    ~^[45]  1;
    default 0;
}

access_log /var/log/nginx/errors.log combined if=$loggable;
```

---

## ModSecurity WAF

Install and enable ModSecurity with OWASP Core Rule Set:

```nginx
# Load module
load_module modules/ngx_http_modsecurity_module.so;

server {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;
}
```

---

## Fail2ban Integration

### NGINX Filter

`/etc/fail2ban/filter.d/nginx-limit-req.conf`:

```ini
[Definition]
failregex = limiting requests, excess: .* by zone .*, client: <HOST>
ignoreregex =
```

### Jail Configuration

`/etc/fail2ban/jail.local`:

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=nginx, port="http,https"]
logpath = /var/log/nginx/error.log
findtime = 60
maxretry = 10
bantime = 3600
```

---

## Security Checklist

- [ ] HTTPS with TLS 1.2+ only
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Hidden files blocked
- [ ] Upload directory PHP blocked
- [ ] Sensitive files protected
- [ ] Admin area IP-restricted
- [ ] Logging configured
- [ ] Fail2ban active
- [ ] Regular updates applied

---

## See Also

- [SSL/TLS Configuration](ssl.md)
- [Pitfalls and Common Mistakes](pitfalls.md)
- [HTTP/3 Configuration](http3.md)

