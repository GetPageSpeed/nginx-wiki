---
title: Red Hat PHP FastCGI
description: PHP FastCGI init script for RHEL/CentOS.
---

# PHP FastCGI Init Script for Red Hat/CentOS

## Setup

```bash
touch /var/run/phpfcgi.pid
chown php:php /var/run/phpfcgi.pid
```

## Init Script

Save as `/etc/init.d/phpfcgi`:

```bash
#!/bin/bash
#
# Startup script for PHP FastCGI
#
# chkconfig: 345 85 15
# description: PHP FastCGI server
# processname: php

. /etc/rc.d/init.d/functions

PHPFCGI="/usr/bin/php-cgi"
FCGIPORT="9000"
FCGIADDR="127.0.0.1"
FCGI_WEB_SERVER_ADDRS="127.0.0.1"
PHP_FCGI_CHILDREN=5
PHP_FCGI_MAX_REQUESTS=1000
ALLOWED_ENV="PATH USER"
PHPUSER=php
PIDFILE=/var/run/phpfcgi.pid

ALLOWED_ENV="$ALLOWED_ENV PHP_FCGI_CHILDREN PHP_FCGI_MAX_REQUESTS FCGI_WEB_SERVER_ADDRS"

case "$1" in
    start)
        echo -n "Starting PHP FastCGI: "
        if [ -z "`id -u $PHPUSER 2> /dev/null`" ]; then
            useradd -s /sbin/nologin $PHPUSER
        fi
        E=
        for i in $ALLOWED_ENV; do E="$E $i=${!i}"; done
        daemon --user $PHPUSER --pidfile $PIDFILE \
            "env - $E $PHPFCGI -q -b $FCGIADDR:$FCGIPORT &> /dev/null &"
        pid=`pidof php-cgi`
        if [ -n "$pid" ]; then
            echo $pid > $PIDFILE
            success
        else
            failure
        fi
        echo
        ;;
    stop)
        echo -n "Stopping PHP FastCGI: "
        killproc -p $PIDFILE phpfcgi
        echo
        ;;
    status)
        status phpfcgi
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
esac

exit 0
```

## Enable

```bash
chmod +x /etc/init.d/phpfcgi
chkconfig phpfcgi on
service phpfcgi start
```


