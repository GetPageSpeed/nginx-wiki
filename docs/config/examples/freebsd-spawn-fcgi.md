---
title: FreeBSD spawn-fcgi
description: Init script for spawn-fcgi on FreeBSD.
---

# FreeBSD spawn-fcgi Init Script

A flexible init script for spawn-fcgi that works with PHP, Python WSGI, CGILua, etc.

!!! tip
    For PHP on FreeBSD, consider using PHP-FPM instead (available in configure options).

## Script

Save as `/usr/local/etc/rc.d/spawn-fcgi`:

```bash
#!/bin/sh
# Modified spawn-fcgi for rc.d
NAME=php-cgi
SPAWNFCGI=/usr/local/bin/spawn-fcgi
FCGI_CHILDREN=3
PROCESS_NAME=lua
SERVER_SOCKET=/tmp/fcgi.socket
SERVER_PID=/tmp/fcgi.pid
SERVER_USER=www
SERVER_GROUP=www
FCGI_PROCESS=/usr/local/bin/php-cgi
SOCKSTAT=/usr/bin/sockstat
GREP=/usr/bin/grep
KILLALL=/usr/bin/killall
cmd=$1

fcgi_restart() {
    fcgi_stop
    fcgi_start
}

fcgi_start() {
    $SPAWNFCGI -s $SERVER_SOCKET -P $SERVER_PID \
        -u $SERVER_USER -g $SERVER_GROUP \
        -F $FCGI_CHILDREN -f $FCGI_PROCESS
}

fcgi_stop() {
    $KILLALL $PROCESS_NAME
}

fcgi_status() {
    $SOCKSTAT -u | $GREP -i $SERVER_SOCKET > /dev/null
    [ $? -eq 0 ] && echo "$PROCESS_NAME is running" || echo "$PROCESS_NAME is not running!"
}

fcgi_help() {
    echo "Usage: $0 {(re)start|status|stop}"
}

case ${cmd} in
    [Rr][Ee][Ss][Tt][Aa][Rr][Tt]) fcgi_restart;;
    [Ss][Tt][Aa][Rr][Tt]) fcgi_start;;
    [Ss][Tt][Oo][Pp]) fcgi_stop;;
    [Ss][Tt][Aa][Tt][Uu][Ss]) fcgi_status;;
    *) fcgi_help;;
esac
```

## Usage

```bash
/usr/local/etc/rc.d/spawn-fcgi start
/usr/local/etc/rc.d/spawn-fcgi status
/usr/local/etc/rc.d/spawn-fcgi stop
```

## Start on Boot

Add to `/etc/rc.local`:

```bash
/usr/local/etc/rc.d/spawn-fcgi start
```

## TCP vs Unix Socket

To use TCP instead of Unix socket, change `SERVER_SOCKET` to a port number and replace `-s` with `-p` in `fcgi_start()`.


