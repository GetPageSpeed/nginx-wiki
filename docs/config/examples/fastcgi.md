---
title: FastCGI Setup
description: An example NGINX configuration that uses FastCGI.
---

# FastCGI Setup

This guide covers setting up FastCGI with NGINX, including spawning processes and securing upload directories.

---

## FastCGI Parameters

Keep your typical FCGI settings in a single file (`/etc/nginx/fastcgi.conf` or `/etc/nginx/fastcgi_params`):

```nginx
# fastcgi.conf
fastcgi_param  GATEWAY_INTERFACE  CGI/1.1;
fastcgi_param  SERVER_SOFTWARE    nginx;
fastcgi_param  QUERY_STRING       $query_string;
fastcgi_param  REQUEST_METHOD     $request_method;
fastcgi_param  CONTENT_TYPE       $content_type;
fastcgi_param  CONTENT_LENGTH     $content_length;
fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;
fastcgi_param  SCRIPT_NAME        $fastcgi_script_name;
fastcgi_param  REQUEST_URI        $request_uri;
fastcgi_param  DOCUMENT_URI       $document_uri;
fastcgi_param  DOCUMENT_ROOT      $document_root;
fastcgi_param  SERVER_PROTOCOL    $server_protocol;
fastcgi_param  REMOTE_ADDR        $remote_addr;
fastcgi_param  REMOTE_PORT        $remote_port;
fastcgi_param  SERVER_ADDR        $server_addr;
fastcgi_param  SERVER_PORT        $server_port;
fastcgi_param  SERVER_NAME        $server_name;
```

!!! tip
    You may want to replace `$document_root` with an actual path to avoid "script not found" errors.

---

## Spawning FastCGI Processes

Unlike Apache or Lighttpd, NGINX does not automatically spawn FCGI processes. You must start them separately.

### Manual Start

```bash
php -b 127.0.0.1:9000
```

### Init Script (Debian/Ubuntu)

```bash
#!/bin/bash
BIND=127.0.0.1:9000
USER=www-data
PHP_FCGI_CHILDREN=15
PHP_FCGI_MAX_REQUESTS=1000

PHP_CGI=/usr/bin/php-cgi
PHP_CGI_NAME=`basename $PHP_CGI`
PHP_CGI_ARGS="- USER=$USER PATH=/usr/bin PHP_FCGI_CHILDREN=$PHP_FCGI_CHILDREN PHP_FCGI_MAX_REQUESTS=$PHP_FCGI_MAX_REQUESTS $PHP_CGI -b $BIND"
RETVAL=0

start() {
    echo -n "Starting PHP FastCGI: "
    start-stop-daemon --quiet --start --background --chuid "$USER" --exec /usr/bin/env -- $PHP_CGI_ARGS
    RETVAL=$?
    echo "$PHP_CGI_NAME."
}

stop() {
    echo -n "Stopping PHP FastCGI: "
    killall -q -w -u $USER $PHP_CGI
    RETVAL=$?
    echo "$PHP_CGI_NAME."
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: php-fastcgi {start|stop|restart}"
        exit 1
        ;;
esac
exit $RETVAL
```

Save to `/etc/init.d/php-fcgi` and install:

```bash
update-rc.d php-fcgi defaults
service php-fcgi start
```

---

## Connecting NGINX to FastCGI

```nginx
location ~ \.php$ {
    include /etc/nginx/fastcgi_params;
    fastcgi_pass 127.0.0.1:9000;
}
```

---

## Securing Upload Directories

!!! danger "Critical Security Issue"
    If someone uploads `xyz.php` to a publicly accessible uploads directory, they can execute arbitrary PHP code on your server!

Prevent PHP execution in upload directories:

```nginx
location ~ \.php$ {
    include /etc/nginx/fastcgi_params;
    if ($uri !~ "^/images/") {
        fastcgi_pass 127.0.0.1:9000;
    }
}
```

Or use a separate location block:

```nginx
# Block PHP in uploads
location ~* ^/uploads/.*\.php$ {
    deny all;
}

# Normal PHP handling
location ~ \.php$ {
    include /etc/nginx/fastcgi_params;
    fastcgi_pass 127.0.0.1:9000;
}
```

!!! tip "Modern Alternative"
    Consider using PHP-FPM (FastCGI Process Manager) instead of spawning php-cgi manually. See the [PHP-FPM guide](../recipes/php-fpm.md).


