---
title: Per-VirtualHost Logging
description: Separate error and access logs for each server block.
---

# Per-VirtualHost Logging

When you have multiple virtual hosts, keep separate logs for each one.

## Configuration

```nginx
error_log logs/main_error.log;

events {
    worker_connections 1024;
}

http {
    error_log logs/http_error.log error;

    server {
        server_name one.org;
        access_log logs/one.access;
        error_log logs/one.error error;
    }

    server {
        server_name two.org;
        access_log logs/two.access;
        error_log logs/two.error error;
    }
}
```

## Example Output

A request for `one.org/nonexistent.html` outputs to `logs/one.error`:

```
2009/01/01 19:45:44 [error] 29874#0: *98 open() "/var/www/one/nonexistent.html" 
failed (2: No such file or directory), client: 11.22.33.44, server: one.org, 
request: "GET /nonexistent.html HTTP/1.1", host: "one.org"
```

!!! note "Log Levels"
    The `error_log` directive has different default values depending on the context. Explicitly set the logging level in each `server { }` block.

## Log Format Customization

You can also customize the access log format per virtual host:

```nginx
http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';

    log_format detailed '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for" '
                        'rt=$request_time urt=$upstream_response_time';

    server {
        server_name api.example.com;
        access_log logs/api.access detailed;
    }

    server {
        server_name www.example.com;
        access_log logs/www.access main;
    }
}
```


