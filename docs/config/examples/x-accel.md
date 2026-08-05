---
title: NGINX X-Accel and X-Sendfile for Protected File Downloads
description: Use NGINX X-Accel-Redirect for internal redirects, protected file downloads, streaming, rate limiting, and backend offloading.
keywords: nginx x-accel, nginx x-sendfile, nginx internal redirect, nginx protected downloads, nginx file serving, x-accel-redirect
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - x-accel
  - x-sendfile
  - file downloads
  - internal redirect
---

# X-Accel (X-Sendfile)

X-Accel allows for internal redirection to a location determined by a header returned from a backend. This is commonly known as **X-Sendfile**.

## How It Works

1. Backend handles authentication, logging, or other logic
2. Backend sends `X-Accel-Redirect` header with an internal URI
3. NGINX serves the file, freeing the backend for other requests
4. End user receives the file directly from NGINX

---

## Basic Configuration

### Using `alias`

```nginx
# Will serve /var/www/files/myfile.tar.gz
# When passed URI /protected_files/myfile.tar.gz
location /protected_files {
    internal;
    alias /var/www/files;
}
```

### Using `root`

```nginx
# Will serve /var/www/protected_files/myfile.tar.gz
# When passed URI /protected_files/myfile.tar.gz
location /protected_files {
    internal;
    root /var/www;
}
```

### Proxying to Another Server

```nginx
location /protected_files {
    internal;
    proxy_pass http://127.0.0.2;
}
```

!!! info "`internal`"
    The `internal` directive prevents direct client access to this location. Only internal redirects (like X-Accel) can reach it.

---

## Special Headers

### X-Accel-Redirect

Sets the URI for NGINX to serve.

```
X-Accel-Redirect: /protected_files/myfile.tar.gz
```

### X-Accel-Buffering

Controls proxy buffering for this connection.

| Value | Effect |
|-------|--------|
| `yes` | Allow response caching (default) |
| `no` | Unbuffered responses (for Comet/streaming) |

```
X-Accel-Buffering: no
```

### X-Accel-Charset

Sets the charset of the file.

```
X-Accel-Charset: utf-8
```

### X-Accel-Expires

Sets when to expire the file in NGINX's internal cache.

| Value | Effect |
|-------|--------|
| `off` | Disable cache expiry (default) |
| `<seconds>` | Expire after N seconds |

```
X-Accel-Expires: 3600
```

### X-Accel-Limit-Rate

Sets rate limit for this single request.

| Value | Effect |
|-------|--------|
| `off` | Unlimited (default) |
| `<bytes>` | Limit to N bytes/second |

```
X-Accel-Limit-Rate: 1024
```

---

## Example: Protected Downloads

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    # Public frontend
    location / {
        proxy_pass http://backend;
    }

    # Protected files (internal only)
    location /protected/ {
        internal;
        alias /var/www/downloads/;
    }
}
```

### Backend Response (e.g., PHP)

```php
<?php
// Verify user has access
if (!user_has_access($file)) {
    http_response_code(403);
    exit;
}

// Log the download
log_download($user, $file);

// Let NGINX serve the file
header('X-Accel-Redirect: /protected/' . $file);
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . basename($file) . '"');
exit;
?>
```


