---
title: NGINX FreeBSD Python Django FastCGI Init Script
description: FreeBSD rc.d init script for Python Django FastCGI with prefork workers, socket management, and automatic startup configuration.
keywords: nginx freebsd python, freebsd django, freebsd fastcgi python, nginx django freebsd, python fcgi script, django runfcgi
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - freebsd
  - python
  - django
  - fastcgi
---

# FreeBSD Python FastCGI Init Script

Save as `/etc/rc.d/python_fcgi`:

```bash
#!/bin/sh
# PROVIDE: python fcgi start up script

. /etc/rc.subr

name="python_fcgi"
rcvar=${name}_enable

project_path="/path/to/your/django/project"
pidfile=/var/run/python-fcgi.pid

load_rc_config ${name}

[ -z "$python_fcgi_enable" ] && python_fcgi_enable="NO"

command=/usr/local/bin/python
command_args="${project_path}/manage.py runfcgi \
    maxchildren=10 maxspare=5 minspare=2 \
    method=prefork socket=/tmp/python_fcgi.sock \
    pidfile=${pidfile} --pythonpath=${project_path}"

python_fcgi_stop() {
    echo "Stopping $name."
    pids=`cat /var/run/python_fcgi.pid`
    kill ${pids}
    wait_for_pids $pids
}

run_rc_command "$1"
chown www:www /tmp/python_fcgi.sock
```

## Configuration

Add to `/etc/rc.conf`:

```bash
python_fcgi_enable="YES"
```


