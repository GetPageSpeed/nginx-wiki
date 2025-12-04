---
title: Ruby on Rails
description: Modern NGINX configuration for Ruby on Rails with Puma or Unicorn.
---

# Ruby on Rails

Production-ready NGINX configuration for Ruby on Rails applications with Puma (recommended) or Unicorn.

---

## With Puma (Recommended)

```nginx
upstream rails {
    server unix:/var/www/myapp/tmp/sockets/puma.sock fail_timeout=0;
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    listen [::]:443 ssl;
    server_name example.com www.example.com;

    root /var/www/myapp/public;

    # SSL
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Logging
    access_log /var/log/nginx/rails.access.log;
    error_log /var/log/nginx/rails.error.log;

    # Max upload size
    client_max_body_size 50m;

    # Asset pipeline (precompiled assets)
    location ^~ /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
        gzip_static on;
        access_log off;
    }

    # Favicon
    location = /favicon.ico {
        expires 1y;
        access_log off;
        log_not_found off;
    }

    # Try static files first, then proxy to Rails
    location / {
        try_files $uri @rails;
    }

    location @rails {
        proxy_pass http://rails;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_redirect off;
        proxy_read_timeout 300;
    }

    # Error pages
    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /var/www/myapp/public;
    }
}
```

### Puma Configuration

`config/puma.rb`:

```ruby
# Puma configuration for production

workers ENV.fetch("WEB_CONCURRENCY") { 2 }
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count

environment ENV.fetch("RAILS_ENV") { "production" }

# Socket binding
app_dir = File.expand_path("../..", __FILE__)
bind "unix://#{app_dir}/tmp/sockets/puma.sock"

# PID and state files
pidfile "#{app_dir}/tmp/pids/puma.pid"
state_path "#{app_dir}/tmp/pids/puma.state"

# Logging
stdout_redirect "#{app_dir}/log/puma.stdout.log",
                "#{app_dir}/log/puma.stderr.log",
                true

# Preload for better memory usage with workers
preload_app!

on_worker_boot do
  ActiveRecord::Base.establish_connection if defined?(ActiveRecord)
end
```

### Systemd Service

`/etc/systemd/system/puma.service`:

```ini
[Unit]
Description=Puma Rails Server
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/myapp
Environment=RAILS_ENV=production
ExecStart=/usr/local/bin/bundle exec puma -C config/puma.rb
ExecReload=/bin/kill -USR1 $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## With Unicorn

```nginx
upstream rails {
    server unix:/var/www/myapp/tmp/sockets/unicorn.sock fail_timeout=0;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    root /var/www/myapp/public;

    # SSL config...

    location ^~ /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }

    location / {
        try_files $uri @rails;
    }

    location @rails {
        proxy_pass http://rails;
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
app_dir = File.expand_path("../..", __FILE__)
working_directory app_dir

worker_processes ENV.fetch("WEB_CONCURRENCY") { 4 }.to_i
timeout 30

listen "#{app_dir}/tmp/sockets/unicorn.sock", backlog: 64
pid "#{app_dir}/tmp/pids/unicorn.pid"

stderr_path "#{app_dir}/log/unicorn.stderr.log"
stdout_path "#{app_dir}/log/unicorn.stdout.log"

preload_app true

before_fork do |server, worker|
  ActiveRecord::Base.connection.disconnect! if defined?(ActiveRecord::Base)
end

after_fork do |server, worker|
  ActiveRecord::Base.establish_connection if defined?(ActiveRecord::Base)
end
```

---

## ActionCable (WebSockets)

```nginx
upstream rails {
    server unix:/var/www/myapp/tmp/sockets/puma.sock;
}

upstream cable {
    server unix:/var/www/myapp/tmp/sockets/cable.sock;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    # SSL config...

    location /cable {
        proxy_pass http://cable;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    location / {
        try_files $uri @rails;
    }

    location @rails {
        proxy_pass http://rails;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Rails Configuration

`config/environments/production.rb`:

```ruby
Rails.application.configure do
  # Force HTTPS
  config.force_ssl = true
  
  # Trust proxy headers
  config.action_dispatch.trusted_proxies = [
    IPAddr.new('127.0.0.1'),
    IPAddr.new('::1')
  ]
  
  # Asset host (optional CDN)
  # config.asset_host = 'https://assets.example.com'
  
  # Serve static files from public/
  config.public_file_server.enabled = ENV['RAILS_SERVE_STATIC_FILES'].present?
end
```

---

## Deployment Tips

### Precompile Assets

```bash
RAILS_ENV=production bundle exec rails assets:precompile
```

### Zero-Downtime Restarts

```bash
# Puma
bundle exec pumactl -S tmp/pids/puma.state restart

# Unicorn
kill -USR2 $(cat tmp/pids/unicorn.pid)
```

---

## See Also

- [Redmine Configuration](redmine.md)
- [Django Configuration](django.md)
