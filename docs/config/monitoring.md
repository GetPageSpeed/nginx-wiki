---
title: Monitoring & Observability
description: Monitor NGINX performance with metrics, logging, and tracing.
---

# Monitoring & Observability

Comprehensive guide to monitoring NGINX performance, health, and traffic.

---

## Status Module

### Basic Status (stub_status)

```nginx
server {
    listen 127.0.0.1:8080;

    location /nginx_status {
        stub_status;
        allow 127.0.0.1;
        deny all;
    }
}
```

Output:
```
Active connections: 291
server accepts handled requests
 16630948 16630948 31070465
Reading: 6 Writing: 179 Waiting: 106
```

| Metric | Description |
|--------|-------------|
| Active connections | Current active connections |
| accepts | Total accepted connections |
| handled | Total handled connections |
| requests | Total requests |
| Reading | Reading request headers |
| Writing | Writing response |
| Waiting | Keep-alive connections |

---

## Prometheus Metrics

### Using nginx-prometheus-exporter

```bash
# Install exporter
docker run -p 9113:9113 nginx/nginx-prometheus-exporter:latest \
    -nginx.scrape-uri=http://nginx:8080/nginx_status
```

### Using VTS Module

Install `nginx-module-vts` for detailed metrics:

```nginx
http {
    vhost_traffic_status_zone;

    server {
        location /status {
            vhost_traffic_status_display;
            vhost_traffic_status_display_format prometheus;
            allow 127.0.0.1;
            deny all;
        }
    }
}
```

### Prometheus Configuration

`prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'nginx-vts'
    static_configs:
      - targets: ['nginx:8080']
    metrics_path: /status/format/prometheus
```

---

## Grafana Dashboards

### Key Metrics to Monitor

| Metric | Description |
|--------|-------------|
| `nginx_connections_active` | Active connections |
| `nginx_connections_accepted` | Accepted connections |
| `nginx_http_requests_total` | Total HTTP requests |
| `nginx_http_request_duration_seconds` | Request latency |
| `nginx_upstream_response_time` | Backend response time |

### Dashboard JSON

Import pre-built dashboards:
- NGINX by stub_status: Dashboard ID 12708
- NGINX VTS: Dashboard ID 2949

---

## Enhanced Logging

### JSON Access Log

```nginx
log_format json_combined escape=json
    '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"remote_user":"$remote_user",'
        '"request":"$request",'
        '"status": "$status",'
        '"body_bytes_sent":"$body_bytes_sent",'
        '"request_time":"$request_time",'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent",'
        '"request_id":"$request_id",'
        '"upstream_response_time":"$upstream_response_time",'
        '"upstream_addr":"$upstream_addr",'
        '"ssl_protocol":"$ssl_protocol",'
        '"ssl_cipher":"$ssl_cipher"'
    '}';

access_log /var/log/nginx/access.json json_combined;
```

### Performance Log

```nginx
log_format performance '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time"';

access_log /var/log/nginx/performance.log performance;
```

### Conditional Logging

```nginx
# Log slow requests only
map $request_time $logslow {
    ~^[0-2]\.      0;
    default        1;
}

access_log /var/log/nginx/slow.log combined if=$logslow;

# Log errors only
map $status $logerror {
    ~^[45]  1;
    default 0;
}

access_log /var/log/nginx/errors.log combined if=$logerror;
```

---

## Log Aggregation

### Filebeat Configuration

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.json
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      service: nginx
      type: access

  - type: log
    enabled: true
    paths:
      - /var/log/nginx/error.log
    fields:
      service: nginx
      type: error

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### Vector Configuration

```toml
[sources.nginx_logs]
type = "file"
include = ["/var/log/nginx/access.json"]

[transforms.parse_nginx]
type = "json_parser"
inputs = ["nginx_logs"]

[sinks.elasticsearch]
type = "elasticsearch"
inputs = ["parse_nginx"]
endpoint = "http://elasticsearch:9200"
index = "nginx-%Y.%m.%d"
```

---

## Request Tracing

### Request ID

```nginx
# Generate request ID if not present
map $http_x_request_id $request_id {
    default $http_x_request_id;
    ""      $request_id;
}

server {
    # Add request ID to logs
    access_log /var/log/nginx/access.log combined;

    location / {
        # Pass to backend
        proxy_set_header X-Request-ID $request_id;
        proxy_pass http://backend;
    }
}
```

### OpenTelemetry Integration

Using `ngx_otel_module`:

```nginx
load_module modules/ngx_otel_module.so;

http {
    otel_exporter {
        endpoint otlp-collector:4317;
    }

    otel_service_name nginx;

    server {
        otel_trace on;
        otel_trace_context propagate;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

---

## Health Checks

### Simple Health Endpoint

```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}

location /ready {
    access_log off;
    return 200 "ready\n";
    add_header Content-Type text/plain;
}
```

### Detailed Health Check

```nginx
location /health {
    access_log off;
    default_type application/json;
    return 200 '{"status":"healthy","timestamp":"$time_iso8601","connections":$connections_active}';
}
```

---

## Alerting

### Alert Rules (Prometheus)

```yaml
groups:
  - name: nginx
    rules:
      - alert: NginxHighErrorRate
        expr: rate(nginx_http_requests_total{status=~"5.."}[5m]) / rate(nginx_http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on NGINX"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: NginxHighLatency
        expr: histogram_quantile(0.99, rate(nginx_http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on NGINX"
          description: "P99 latency is {{ $value }}s"

      - alert: NginxDown
        expr: nginx_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "NGINX is down"
```

---

## Real-Time Monitoring

### GoAccess (Terminal)

```bash
# Real-time log analysis
goaccess /var/log/nginx/access.log -o /var/www/html/report.html \
    --real-time-html --ws-url=wss://stats.example.com:7890

# JSON log format
goaccess /var/log/nginx/access.json \
    --log-format='{"time_local":"%d/%b/%Y:%T %z","remote_addr":"%h","request":"%r","status":%s,"body_bytes_sent":%b,"request_time":"%T","http_referrer":"%R","http_user_agent":"%u"}'
```

### ngxtop

```bash
# Install
pip install ngxtop

# Real-time monitoring
ngxtop -l /var/log/nginx/access.log

# Filter by status
ngxtop -l /var/log/nginx/access.log --filter 'status >= 400'
```

---

## Performance Benchmarking

### Built-in Variables

```nginx
# Add timing info to response headers (debugging)
add_header X-Request-Time $request_time;
add_header X-Upstream-Time $upstream_response_time;
```

### wrk Benchmarking

```bash
# Basic test
wrk -t12 -c400 -d30s http://localhost/

# With Lua script for POST requests
wrk -t12 -c400 -d30s -s post.lua http://localhost/api
```

### ab (Apache Bench)

```bash
ab -n 10000 -c 100 http://localhost/
```

---

## Key Metrics Dashboard

| Category | Metric | Warning | Critical |
|----------|--------|---------|----------|
| Traffic | Requests/sec | >1000 | >5000 |
| Errors | 5xx rate | >1% | >5% |
| Latency | P99 | >500ms | >1s |
| Connections | Active | >1000 | >5000 |
| Upstream | Response time | >200ms | >500ms |

---

## Log Rotation

```nginx
# /etc/logrotate.d/nginx
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
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}
```

---

## See Also

- [Security Hardening](security.md)
- [Load Balancing](load-balancing.md)
- [Debugging Guide](debugging.md)

