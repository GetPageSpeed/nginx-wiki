---
title: Init Scripts
description: Various useful init scripts for starting NGINX.
---

# NGINX Init Scripts

There are many ways to start NGINX. If you install from a repository, an init script is likely included. If you installed from source, you'll need one of these:

---

## Systemd (Recommended)

Most modern Linux distributions use systemd. See the [systemd service file](systemd.md) guide.

---

## Linux SysVinit

### Red Hat / CentOS / Fedora

Save as `/etc/init.d/nginx`:

```bash
#!/bin/sh
#
# nginx - This shell script manages the nginx web server
#
# chkconfig: - 85 15
# description: NGINX is an HTTP and reverse proxy server
# processname: nginx
# config: /etc/nginx/nginx.conf
# pidfile: /var/run/nginx.pid

. /etc/rc.d/init.d/functions

NGINX=/usr/sbin/nginx
CONF=/etc/nginx/nginx.conf
PIDFILE=/var/run/nginx.pid

start() {
    echo -n "Starting nginx: "
    daemon $NGINX -c $CONF
    RETVAL=$?
    echo
    return $RETVAL
}

stop() {
    echo -n "Stopping nginx: "
    killproc -p $PIDFILE nginx -QUIT
    RETVAL=$?
    echo
    return $RETVAL
}

reload() {
    echo -n "Reloading nginx: "
    killproc -p $PIDFILE nginx -HUP
    RETVAL=$?
    echo
    return $RETVAL
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
    reload)
        reload
        ;;
    status)
        status -p $PIDFILE nginx
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status}"
        exit 1
esac

exit $RETVAL
```

Install:

```bash
chmod +x /etc/init.d/nginx
chkconfig --add nginx
chkconfig nginx on
```

---

## Upstart (Ubuntu < 15.04)

Save as `/etc/init/nginx.conf`:

```
description "nginx http daemon"

start on (filesystem and net-device-up IFACE!=lo)
stop on runlevel [!2345]

env DAEMON=/usr/sbin/nginx
env PIDFILE=/var/run/nginx.pid

expect fork
respawn
respawn limit 10 5

pre-start script
    $DAEMON -t
    if [ $? -ne 0 ]; then
        exit $?
    fi
end script

exec $DAEMON
```

---

## FreeBSD rc.d

Save as `/usr/local/etc/rc.d/nginx`:

```sh
#!/bin/sh

# PROVIDE: nginx
# REQUIRE: LOGIN cleanvar
# KEYWORD: shutdown

. /etc/rc.subr

name="nginx"
rcvar=nginx_enable
load_rc_config $name

: ${nginx_enable="NO"}
: ${nginx_pidfile="/var/run/nginx.pid"}

command="/usr/local/sbin/nginx"
pidfile="${nginx_pidfile}"
required_files="/usr/local/etc/nginx/nginx.conf"

start_precmd="nginx_checkconfig"
reload_cmd="nginx_reload"
configtest_cmd="nginx_checkconfig"
extra_commands="reload configtest"

nginx_checkconfig() {
    ${command} -t
}

nginx_reload() {
    ${command} -s reload
}

run_rc_command "$1"
```

Enable:

```bash
echo 'nginx_enable="YES"' >> /etc/rc.conf
```

---

## macOS launchd

Save as `/Library/LaunchDaemons/org.nginx.nginx.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>org.nginx.nginx</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/nginx</string>
        <string>-g</string>
        <string>daemon off;</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/var/log/nginx/error.log</string>
</dict>
</plist>
```

Load:

```bash
sudo launchctl load /Library/LaunchDaemons/org.nginx.nginx.plist
```

---

## Windows

Use NSSM (Non-Sucking Service Manager) to run NGINX as a Windows service:

```batch
nssm install nginx "C:\nginx\nginx.exe"
nssm set nginx AppDirectory "C:\nginx"
nssm start nginx
```

See [PHP on Windows](windows-php.md) for additional Windows configuration.


