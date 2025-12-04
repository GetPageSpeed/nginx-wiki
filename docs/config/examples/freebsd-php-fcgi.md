---
title: FreeBSD PHP FastCGI
description: PHP FastCGI init script for FreeBSD.
---

# FreeBSD PHP FastCGI Init Script

Save as `/etc/rc.d/phpfcgid`:

```bash
#!/bin/sh

# PROVIDE: phpfcgid
# REQUIRE: LOGIN
# KEYWORD: shutdown

. /etc/rc.subr

name="phpfcgid"
rcvar=`set_rcvar`

load_rc_config $name
: ${phpfcgid_enable="NO"}
: ${phpfcgid_users="www"}
: ${phpfcgid_children="2"}
: ${phpfcgid_tmpdir="/tmp"}
: ${phpfcgid_requests="500"}

restart_cmd=phpfcgid_restart
start_cmd=phpfcgid_start
stop_cmd=phpfcgid_stop

phpfcgid_start() {
    echo "Starting $name with ${phpfcgid_children} children."
    export PHP_FCGI_CHILDREN=${phpfcgid_children}
    export PHP_FCGI_MAX_REQUESTS=${phpfcgid_requests}
    for user in ${phpfcgid_users}; do
        socketdir="${phpfcgid_tmpdir}/.fastcgi.${user}"
        mkdir -p ${socketdir}
        chown ${user}:www ${socketdir}
        chmod 0750 ${socketdir}
        su -m ${user} -c "/usr/local/bin/php-cgi -b ${socketdir}/socket&"
    done
}

phpfcgid_stop() {
    echo "Stopping $name."
    pids=`pgrep php-cgi`
    pkill php-cgi
    wait_for_pids $pids
}

phpfcgid_restart() {
    phpfcgid_stop
    phpfcgid_start
}

run_rc_command "$1"
```

## Configuration

Add to `/etc/rc.conf`:

```bash
phpfcgid_enable="YES"
phpfcgid_users="www"
phpfcgid_children="5"
```


