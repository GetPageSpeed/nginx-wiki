---
title: NGINX Redmine Configuration Guide
description: Production-ready NGINX configuration for Redmine project management with Puma or Unicorn Ruby application servers.
keywords: nginx, redmine, project management, ruby, puma, unicorn, issue tracking, ruby on rails, agile
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - redmine
  - ruby
  - project management
  - puma
  - unicorn
---

# Redmine

Production-ready NGINX configuration for Redmine with Puma or Unicorn Ruby application servers.

---

## With Puma (Recommended)

```nginx
upstream redmine {
    server unix:/var/www/redmine/tmp/sockets/puma.sock fail_timeout=0;
}

server {
    listen 443 ssl;
    http2 on;
    server_name redmine.example.com;

    root /var/www/redmine/public;

    # SSL
    ssl_certificate /etc/letsencrypt/live/redmine.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/redmine.example.com/privkey.pem;

    # File upload limit
    client_max_body_size 100m;

    # Static files
    location ~ ^/(assets|images|javascripts|stylesheets|plugin_assets)/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        try_files $uri @redmine;
    }

    location @redmine {
        proxy_pass http://redmine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts for large attachments
        proxy_read_timeout 300;
        proxy_connect_timeout 60;
    }
}
```

### Puma Configuration

`config/puma.rb`:

```ruby
workers ENV.fetch("WEB_CONCURRENCY") { 2 }
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count

environment ENV.fetch("RAILS_ENV") { "production" }

bind "unix:///var/www/redmine/tmp/sockets/puma.sock"
pidfile "/var/www/redmine/tmp/pids/puma.pid"
state_path "/var/www/redmine/tmp/pids/puma.state"

activate_control_app
```

---

## With Unicorn

```nginx
upstream redmine {
    server unix:/var/www/redmine/tmp/sockets/unicorn.sock fail_timeout=0;
}

server {
    listen 443 ssl;
    http2 on;
    server_name redmine.example.com;

    root /var/www/redmine/public;

    # SSL config...

    location ~ ^/(assets|images|javascripts|stylesheets|plugin_assets)/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        try_files $uri @redmine;
    }

    location @redmine {
        proxy_pass http://redmine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Unicorn Configuration

`config/unicorn.rb`:

```ruby
worker_processes 4
working_directory "/var/www/redmine"
listen "/var/www/redmine/tmp/sockets/unicorn.sock", backlog: 64
timeout 30
pid "/var/www/redmine/tmp/pids/unicorn.pid"
stderr_path "/var/www/redmine/log/unicorn.stderr.log"
stdout_path "/var/www/redmine/log/unicorn.stdout.log"

preload_app true
```

---

## Systemd Service

`/etc/systemd/system/redmine.service`:

```ini
[Unit]
Description=Redmine Puma Server
After=network.target

[Service]
Type=simple
User=redmine
Group=redmine
WorkingDirectory=/var/www/redmine
Environment=RAILS_ENV=production
ExecStart=/usr/local/bin/bundle exec puma -C config/puma.rb
ExecReload=/bin/kill -USR1 $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## See Also

- [Ruby Applications](ruby.md)
- [Java/Tomcat Configuration](java-servers.md)
