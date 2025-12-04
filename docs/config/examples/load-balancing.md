---
title: Simple Load Balancing
---

# Simple Load Balancing

An example NGINX configuration that performs simple load balancing across multiple backend servers.

## nginx.conf

```nginx
http {
  upstream myproject {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;    
    server 127.0.0.1:8003;
  }

  server {
    listen 80;
    server_name www.domain.com;
    location / {
      proxy_pass http://myproject;
    }
  }
}
```

## Key points

- The `upstream` block defines a group of backend servers.
- The `weight` parameter controls load distribution (higher weight = more requests).
- By default, NGINX uses round-robin load balancing.
- Other load balancing methods include `least_conn`, `ip_hash`, and `hash`.


